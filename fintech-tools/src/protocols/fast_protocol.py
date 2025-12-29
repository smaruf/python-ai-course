"""
FAST Protocol Implementation

FIX Adapted for STreaming (FAST) Protocol for efficient market data encoding
"""

from typing import Dict, Any, Optional, List
import struct


class FASTProtocol:
    """
    FAST Protocol encoder/decoder
    
    FAST is a compression technique for FIX messages, particularly useful
    for high-frequency market data distribution.
    """
    
    def __init__(self):
        self.templates: Dict[int, Dict[str, Any]] = {}
        self.previous_values: Dict[str, Any] = {}
    
    def register_template(
        self,
        template_id: int,
        template_name: str,
        fields: List[Dict[str, Any]]
    ):
        """
        Register a message template
        
        Args:
            template_id: Unique template identifier
            template_name: Template name
            fields: List of field definitions
        """
        self.templates[template_id] = {
            "name": template_name,
            "fields": fields
        }
    
    def encode_uint32(self, value: int) -> bytes:
        """
        Encode unsigned 32-bit integer in FAST format
        
        Args:
            value: Integer value to encode
            
        Returns:
            bytes: Encoded bytes
        """
        result = bytearray()
        
        # Split into 7-bit chunks
        while value >= 0x80:
            result.append((value & 0x7F))
            value >>= 7
        
        # Last byte has high bit set
        result.append(value | 0x80)
        
        return bytes(result)
    
    def decode_uint32(self, data: bytes, offset: int = 0) -> tuple:
        """
        Decode FAST unsigned 32-bit integer
        
        Args:
            data: Encoded bytes
            offset: Starting offset
            
        Returns:
            tuple: (decoded_value, bytes_consumed)
        """
        value = 0
        shift = 0
        bytes_consumed = 0
        
        for byte in data[offset:]:
            bytes_consumed += 1
            value |= (byte & 0x7F) << shift
            
            if byte & 0x80:  # Stop bit set
                break
            
            shift += 7
        
        return value, bytes_consumed
    
    def encode_string(self, value: str) -> bytes:
        """
        Encode string in FAST format
        
        Args:
            value: String to encode
            
        Returns:
            bytes: Encoded bytes
        """
        if not value:
            return b'\x80'  # Null string
        
        encoded = value.encode('ascii')
        result = bytearray(encoded)
        
        # Set stop bit on last byte
        result[-1] |= 0x80
        
        return bytes(result)
    
    def decode_string(self, data: bytes, offset: int = 0) -> tuple:
        """
        Decode FAST string
        
        Args:
            data: Encoded bytes
            offset: Starting offset
            
        Returns:
            tuple: (decoded_string, bytes_consumed)
        """
        result = bytearray()
        bytes_consumed = 0
        
        for byte in data[offset:]:
            bytes_consumed += 1
            result.append(byte & 0x7F)
            
            if byte & 0x80:  # Stop bit set
                break
        
        return result.decode('ascii'), bytes_consumed
    
    def encode_message(
        self,
        template_id: int,
        fields: Dict[str, Any],
        use_delta: bool = True
    ) -> bytes:
        """
        Encode a message using FAST compression
        
        Args:
            template_id: Template ID to use
            fields: Field values
            use_delta: Use delta encoding
            
        Returns:
            bytes: Encoded message
        """
        if template_id not in self.templates:
            raise ValueError(f"Unknown template ID: {template_id}")
        
        template = self.templates[template_id]
        result = bytearray()
        
        # Encode template ID
        result.extend(self.encode_uint32(template_id))
        
        # Encode fields
        for field_def in template["fields"]:
            field_name = field_def["name"]
            field_type = field_def["type"]
            
            value = fields.get(field_name)
            
            if value is None:
                # Null value
                result.append(0x80)
                continue
            
            # Apply delta encoding if enabled
            if use_delta and field_name in self.previous_values:
                if field_type == "uint32":
                    delta = value - self.previous_values[field_name]
                    result.extend(self.encode_uint32(delta))
                elif field_type == "string":
                    # Simple approach: encode full string if changed
                    if value != self.previous_values[field_name]:
                        result.extend(self.encode_string(value))
            else:
                # Full encoding
                if field_type == "uint32":
                    result.extend(self.encode_uint32(value))
                elif field_type == "string":
                    result.extend(self.encode_string(value))
                elif field_type == "decimal":
                    # Simplified decimal encoding (exponent + mantissa)
                    exponent = -2  # Two decimal places
                    mantissa = int(value * 100)
                    result.extend(self.encode_uint32(exponent & 0xFF))
                    result.extend(self.encode_uint32(mantissa))
            
            # Store for delta encoding
            self.previous_values[field_name] = value
        
        return bytes(result)
    
    def decode_message(self, data: bytes) -> Dict[str, Any]:
        """
        Decode a FAST message
        
        Args:
            data: Encoded message
            
        Returns:
            Dict: Decoded field values
        """
        offset = 0
        
        # Decode template ID
        template_id, consumed = self.decode_uint32(data, offset)
        offset += consumed
        
        if template_id not in self.templates:
            raise ValueError(f"Unknown template ID: {template_id}")
        
        template = self.templates[template_id]
        result = {"_template_id": template_id, "_template_name": template["name"]}
        
        # Decode fields
        for field_def in template["fields"]:
            field_name = field_def["name"]
            field_type = field_def["type"]
            
            if offset >= len(data):
                break
            
            if field_type == "uint32":
                value, consumed = self.decode_uint32(data, offset)
                offset += consumed
                result[field_name] = value
            elif field_type == "string":
                value, consumed = self.decode_string(data, offset)
                offset += consumed
                result[field_name] = value
            elif field_type == "decimal":
                # Decode exponent and mantissa
                exponent, consumed = self.decode_uint32(data, offset)
                offset += consumed
                mantissa, consumed = self.decode_uint32(data, offset)
                offset += consumed
                result[field_name] = mantissa / (10 ** abs(exponent))
        
        return result
    
    def create_market_data_template(self):
        """Create a standard market data template"""
        self.register_template(
            template_id=1,
            template_name="MarketData",
            fields=[
                {"name": "symbol", "type": "string"},
                {"name": "bid_price", "type": "decimal"},
                {"name": "ask_price", "type": "decimal"},
                {"name": "bid_size", "type": "uint32"},
                {"name": "ask_size", "type": "uint32"},
                {"name": "last_price", "type": "decimal"},
                {"name": "volume", "type": "uint32"},
            ]
        )
