import ctypes
import multiprocessing as mp
import queue
import time

from ui_components import BlockBase, EndBlock, CondBlock, StartBlock

from .io_interface import NonBlockingLink
from .nodes import Node
from .parser import full_compilation, ExecutionError
from .values import to_boolean


class RunnerError(Exception):
    def __init__(self, name, msg=None):
        if isinstance(name, ExecutionError):
            self.name_ = name.name
            self.msg_ = name.msg
            self.exe_err = name
        else:
            self.name_ = name
            self.msg_ = msg
            self.exe_err = ExecutionError(name, msg)
        super().__init__(self.name_ + ":" + self.msg_)


class Runner:
    def __init__(self, start_block: BlockBase, delay=None):
        self.start_block = start_block
        self.blocks = self.get_blocks()
        self._delay = delay or 0
        self._delay_value = None
        self._current_block = None
        self._is_paused = None
        self._error_occurred = None
        self.out_q = mp.Queue()
        self.err_q = mp.Queue()
        self.in_q = None
        self.link_in_msg = None
        self.link_out_msg = None
        self.sym_table_vars = None
        self.sym_table = None
        self._process: mp.Process | None = None
        self.ast_map = {}

        for block in self.blocks:
            ast = full_compilation(block)
            if isinstance(ast, ExecutionError):
                raise RunnerError(ast)
            if isinstance(block, CondBlock):
                self.ast_map[id(block)] = (ast, (id(block.on_true.next_block), id(block.on_false.next_block)))
            else:
                self.ast_map[id(block)] = (ast, id(block.next_block))

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value
        if self._delay_value is not None:
            self._delay_value.value = value

    @property
    def is_paused(self):
        if self._is_paused is None:
            return False
        return self._is_paused.value

    @property
    def error_occurred(self):
        if self._error_occurred is None:
            return False
        return self._error_occurred.value

    @property
    def current_block(self):
        if self._current_block is None:
            return -1
        return self._current_block.value

    @staticmethod
    def execute_blocks(
            first_block: int,  # the first block to execute
            ast_map: dict[int, tuple[Node, int | tuple[int, int]]],  # list of blocks with their original ids
            delay: mp.Value,  # delay in seconds between blocks
            current_block: mp.Value,  # set to the id of the block being currently executed
            is_paused: mp.Value,  # set to whether the execution is paused
            error_occurred: mp.Value,  # set to whether an error has occurred
            out_q: mp.Queue,  # queue for stdout messages, populated by the runner
            err_q: mp.Queue,  # queue for stderr messages, populated by the runner
            in_q: mp.Queue,  # queue for stdin messages, populated externally
            link_in_msg: mp.Queue,  # messages to send to the IO link
            link_out_msg: mp.Queue,  # messages sent by the IO link
            sym_table_vars: mp.Queue,  # queue for symbol table values, populated by the runner
    ):
        io_link = NonBlockingLink(out_q, err_q, in_q, link_in_msg, link_out_msg)
        current_block.value = first_block
        curr_block_id = first_block
        sym_table = {}
        error_occurred_v = False

        while curr_block_id in ast_map:
            ast, next_block = ast_map[curr_block_id]
            value = ast.evaluate(sym_table, io_link)
            if value.error():
                err_q.put_nowait((value.value.name, value.value.msg, value.value.fmt_args))
                error_occurred.value = True
                error_occurred_v = True
                break

            for key, value in sym_table.items():
                sym_table_vars.put_nowait((key, value.value))

            sym_table_vars.put_nowait(None)
            time.sleep(delay.value)

            while is_paused.value:
                pass

            if isinstance(next_block, int):
                curr_block_id = next_block
                current_block.value = next_block
                continue
            boolean_value = to_boolean(value)
            if value.error():
                err_q.put_nowait((value.value.name, value.value.msg))
                break
            if boolean_value.value:
                curr_block_id = next_block[0]
            else:
                curr_block_id = next_block[1]
            current_block.value = curr_block_id

        if error_occurred_v:
            while True:
                pass

    def get_blocks(self):
        blocks_checked = []
        blocks_to_check = [self.start_block]
        for block in blocks_to_check:
            if isinstance(block, EndBlock) or block in blocks_checked:
                continue
            if isinstance(block, CondBlock):
                if block.on_true.next_block is None or block.on_false.next_block is None:
                    raise RunnerError("error.name.comp_error", "error.msg.incomplete_tree")
                blocks_checked.append(block)
                blocks_to_check.append(block.on_true.next_block)
                blocks_to_check.append(block.on_false.next_block)
            else:
                if block.next_block is None:
                    raise RunnerError("error.name.comp_error", "error.msg.incomplete_tree")
                blocks_checked.append(block)
                blocks_to_check.append(block.next_block)
        blocks_checked = [b for b in blocks_checked if not isinstance(b, EndBlock) and not isinstance(b, StartBlock)]
        return blocks_checked

    def start(self):
        if self._process is not None:
            return

        self._delay_value = mp.Value(ctypes.c_double, self._delay)
        self._current_block = mp.Value(ctypes.c_longlong, 0)
        self._is_paused = mp.Value(ctypes.c_bool, False)
        self._error_occurred = mp.Value(ctypes.c_bool, False)
        self.in_q = mp.Queue()
        self.link_in_msg = mp.Queue()
        self.link_out_msg = mp.Queue()
        self.sym_table_vars = mp.Queue()
        self.sym_table = {}

        self._process = mp.Process(
            target=self.execute_blocks,
            args=(
                id(self.start_block.next_block),
                self.ast_map,
                self._delay_value,
                self._current_block,
                self._is_paused,
                self._error_occurred,
                self.out_q,
                self.err_q,
                self.in_q,
                self.link_in_msg,
                self.link_out_msg,
                self.sym_table_vars
            )
        )

        self._process.start()

    def stop(self):
        if self._process.is_alive():
            self._process.terminate()

        self._delay_value = None
        self._current_block = None
        self._is_paused = None
        self.in_q = None
        self.link_in_msg = None
        self.link_out_msg = None
        self.sym_table_vars = None
        self.sym_table = None

    def update_state(self):
        if self._process is None:
            return
        elif not self._process.is_alive():
            self.stop()
            return

        try:
            # update at most 50 variables per frame
            for _ in range(50):
                value = self.sym_table_vars.get_nowait()
                if value is None:
                    break
                self.sym_table[value[0]] = value[1]
        except queue.Empty:
            pass

    def is_running(self):
        return self._process is not None and self._process.is_alive()

    def pause(self):
        if self.is_paused:
            return

        self._is_paused.value = True

    def resume(self):
        if not self.is_paused:
            return
        self._is_paused.value = False

    def get_queued_messages(self):
        messages = []
        try:
            # get at most 50 messages per frame
            for _ in range(50):
                value = self.out_q.get_nowait()
                messages.append(value)
        except queue.Empty:
            pass
        return messages

    def get_queued_errors(self):
        errors = []
        try:
            for _ in range(50):
                err_name, err_msg, fmt_args = self.err_q.get_nowait()
                errors.append(ExecutionError(err_name, err_msg, **fmt_args))
        except queue.Empty:
            pass
        return errors

    def get_placeholder_text(self):
        if not self.is_running():
            return None

        placeholder = None
        try:
            for _ in range(50):
                _, placeholder = self.link_out_msg.get_nowait()
        except queue.Empty:
            pass
        return placeholder
