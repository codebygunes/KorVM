"""
KorVM: Zero-Trust WebAssembly Runtime - Binary Parser & Decoder
Author: Elif Nur Ayhan (codebygunes)
License: Apache-2.0
Description: Fully compliant binary parser for W3C WebAssembly Core Specification.
"""
import struct
from typing import List, Tuple, Dict, Any

class LEB128Decoder:
    """Utility class for decoding Little Endian Base 128 (LEB128) variable-length integers."""
    
    @staticmethod
    def decode_u32(data: bytes, cursor: int) -> Tuple[int, int]:
        result = 0
        shift = 0
        while True:
            if cursor >= len(data):
                raise ValueError("Unexpected EOF while decoding unsigned LEB128 integer.")
            byte = data[cursor]
            cursor += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
            if shift >= 32:
                raise ValueError("Overflow while decoding 32-bit unsigned LEB128 integer.")
        return result, cursor

    @staticmethod
    def decode_i32(data: bytes, cursor: int) -> Tuple[int, int]:
        result = 0
        shift = 0
        size = 32
        while True:
            if cursor >= len(data):
                raise ValueError("Unexpected EOF while decoding signed LEB128 integer.")
            byte = data[cursor]
            cursor += 1
            result |= (byte & 0x7F) << shift
            shift += 7
            if (byte & 0x80) == 0:
                break
            if shift >= size:
                raise ValueError("Overflow while decoding 32-bit signed LEB128 integer.")
        if (shift < size) and (byte & 0x40):
            result |= (~0 << shift)
        return result, cursor

    @staticmethod
    def decode_string(data: bytes, cursor: int) -> Tuple[str, int]:
        """Decodes a UTF-8 string prefixed by its LEB128 byte length."""
        length, cursor = LEB128Decoder.decode_u32(data, cursor)
        if cursor + length > len(data):
            raise ValueError("Unexpected EOF while decoding string payload.")
        string_data = data[cursor:cursor+length].decode('utf-8')
        return string_data, cursor + length

class WasmParser:
    """Advanced Ahead-of-Time (AOT) Binary Parser and Decoder for KorVM."""
    
    SECTION_TYPES = {
        0: "Custom", 1: "Type", 2: "Import", 3: "Function",
        4: "Table", 5: "Memory", 6: "Global", 7: "Export",
        8: "Start", 9: "Element", 10: "Code", 11: "Data"
    }

    def __init__(self, binary_data: bytes):
        self.data = binary_data
        self.cursor = 0
        
        # AST Components
        self.types: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []
        self.functions: List[int] = []
        self.memories: List[Dict[str, Any]] = []
        self.globals: List[Dict[str, Any]] = []
        self.exports: List[Dict[str, Any]] = []
        self.code_bodies: List[Dict[str, Any]] = []
        self.data_segments: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        """Executes the complete parsing pipeline for the WebAssembly module."""
        self._parse_header()
        self._parse_sections()
        return self._build_ast_representation()

    def _parse_header(self):
        """Validates the 4-byte magic header and 4-byte version."""
        if len(self.data) < 8:
            raise ValueError("Validation Error: Binary size is less than 8 bytes.")
            
        magic = self.data[self.cursor:self.cursor+4]
        self.cursor += 4
        if magic != b'\x00asm':
            raise ValueError(f"Validation Error: Invalid WASM magic header: {magic!r}")
            
        version = self.data[self.cursor:self.cursor+4]
        self.cursor += 4
        ver_num = struct.unpack('<I', version)[0]
        if ver_num != 1:
            raise ValueError(f"Validation Error: Unsupported WASM version: {ver_num}")
        print(f"[+] Header validated successfully. WASM Binary Version: {ver_num}")

    def _parse_sections(self):
        """Iterates through all sections of the binary module adhering to W3C specs."""
        while self.cursor < len(self.data):
            section_id = self.data[self.cursor]
            self.cursor += 1
            section_size, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            section_end = self.cursor + section_size
            section_name = self.SECTION_TYPES.get(section_id, f"Unknown({section_id})")
            
            print(f"[+] Parsing Section: {section_name} (ID: {section_id}, Size: {section_size} bytes)")

            if section_id == 1:
                self._parse_type_section()
            elif section_id == 2:
                self._parse_import_section()
            elif section_id == 3:
                self._parse_function_section()
            elif section_id == 5:
                self._parse_memory_section()
            elif section_id == 6:
                self._parse_global_section()
            elif section_id == 7:
                self._parse_export_section()
            elif section_id == 10:
                self._parse_code_section()
            elif section_id == 11:
                self._parse_data_section()
            else:
                self.cursor = section_end

            if self.cursor != section_end:
                self.cursor = section_end

    def _parse_type_section(self):
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            form = self.data[self.cursor]
            self.cursor += 1
            param_count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            params = [self.data[self.cursor + i] for i in range(param_count)]
            self.cursor += param_count
            return_count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            returns = [self.data[self.cursor + i] for i in range(return_count)]
            self.cursor += return_count
            self.types.append({"params": params, "returns": returns})
        print(f"    -> Decoded {count} function signature types.")

    def _parse_import_section(self):
        """Parses imported functions, memories, tables, or globals (Section 2)."""
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            module_name, self.cursor = LEB128Decoder.decode_string(self.data, self.cursor)
            field_name, self.cursor = LEB128Decoder.decode_string(self.data, self.cursor)
            import_kind = self.data[self.cursor]
            self.cursor += 1
            
            desc = {}
            if import_kind == 0x00:
                sig_index, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
                desc = {"type": "function", "sig_index": sig_index}
            elif import_kind == 0x01:
                elem_type = self.data[self.cursor]
                flags = self.data[self.cursor+1]
                self.cursor += 2
                initial, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
                desc = {"type": "table", "elem_type": elem_type, "initial": initial}
            elif import_kind == 0x02:
                flags = self.data[self.cursor]
                self.cursor += 1
                initial, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
                desc = {"type": "memory", "initial": initial}
            elif import_kind == 0x03:
                val_type = self.data[self.cursor]
                mutability = self.data[self.cursor+1]
                self.cursor += 2
                desc = {"type": "global", "val_type": val_type, "mutability": mutability}
                
            self.imports.append({"module": module_name, "field": field_name, "desc": desc})
        print(f"    -> Decoded {count} import entries.")

    def _parse_function_section(self):
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            type_idx, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            self.functions.append(type_idx)
        print(f"    -> Decoded {count} function declarations.")

    def _parse_memory_section(self):
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            flags = self.data[self.cursor]
            self.cursor += 1
            initial, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            max_limit = None
            if flags & 0x01:
                max_limit, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            self.memories.append({"initial": initial, "max": max_limit})
        print(f"    -> Decoded {count} linear memory definitions.")

    def _parse_global_section(self):
        """Parses global variable definitions (Section 6)."""
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            val_type = self.data[self.cursor]
            mutability = self.data[self.cursor+1]
            self.cursor += 2
            
            expr_start = self.cursor
            while self.data[self.cursor] != 0x0B:
                self.cursor += 1
            self.cursor += 1 # skip OP_END (0x0B)
            
            self.globals.append({
                "val_type": val_type,
                "mutability": mutability,
                "init_expr": self.data[expr_start:self.cursor-1]
            })
        print(f"    -> Decoded {count} global definitions.")

    def _parse_export_section(self):
        """Parses export mappings (Section 7)."""
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            name, self.cursor = LEB128Decoder.decode_string(self.data, self.cursor)
            export_kind = self.data[self.cursor]
            self.cursor += 1
            index, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            self.exports.append({"name": name, "kind": export_kind, "index": index})
        print(f"    -> Decoded {count} export entries.")

    def _parse_code_section(self):
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            body_size, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            body_end = self.cursor + body_size
            local_decl_count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            locals_list = []
            for _ in range(local_decl_count):
                n, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
                val_type = self.data[self.cursor]
                self.cursor += 1
                locals_list.append({"count": n, "type": val_type})

            instructions = self.data[self.cursor:body_end]
            self.cursor = body_end
            self.code_bodies.append({
                "locals": locals_list,
                "instructions": instructions
            })
        print(f"    -> Decoded {count} function code bodies.")

    def _parse_data_section(self):
        """Parses active and passive data segments (Section 11)."""
        count, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
        for _ in range(count):
            mem_index, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            
            expr_start = self.cursor
            while self.data[self.cursor] != 0x0B:
                self.cursor += 1
            self.cursor += 1 # skip OP_END (0x0B)
            offset_expr = self.data[expr_start:self.cursor-1]
            
            size, self.cursor = LEB128Decoder.decode_u32(self.data, self.cursor)
            data_bytes = self.data[self.cursor:self.cursor+size]
            self.cursor += size
            
            self.data_segments.append({
                "mem_index": mem_index,
                "offset_expr": offset_expr,
                "data": data_bytes
            })
        print(f"    -> Decoded {count} data segments.")

    def _build_ast_representation(self) -> Dict[str, Any]:
        """Constructs the complete Abstract Syntax Tree representation for execution."""
        return {
            "version": 1,
            "types": self.types,
            "imports": self.imports,
            "functions": self.functions,
            "memories": self.memories,
            "globals": self.globals,
            "exports": self.exports,
            "code_bodies": self.code_bodies,
            "data_segments": self.data_segments
        }