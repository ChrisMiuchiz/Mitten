import struct
import io
import zlib
from CubeTypes.LongVector3 import LongVector3
from CubeTypes.FloatVector3 import FloatVector3
from CubeTypes.Appearance import Appearance
from CubeTypes.IntVector3 import IntVector3
from CubeTypes.Item import Item
from CubeTypes.Equipment import Equipment
from CubeTypes.StatMultipliers import StatMultipliers

class MockType():
    def __init__(self, field_name, type_or_packstring, byte_padding=None, multi_field_packstring=False):
        self.field_name = field_name
        self.type_or_packstring = type_or_packstring
        self.byte_padding = byte_padding
        self.multi_field_packstring = multi_field_packstring

        self.isTypeValue = hasattr(self.type_or_packstring, 'Import')
        if self.isTypeValue:
            self.data_size = self.type_or_packstring.size
        else:
            self.data_size = struct.calcsize(self.type_or_packstring)

    def Read(self, rdr):
        # Import / unpack
        if self.isTypeValue:
            val = self.type_or_packstring.Import(rdr)
        else:
            val = struct.unpack(self.type_or_packstring, rdr.read(self.data_size))
            if self.multi_field_packstring == False:
                val = val[0]

        # Handle pad bytes.
        if self.byte_padding:
            rdr.read(byte_padding)

        return val

    def Write(self, wtr, read_val):
        if self.isTypeValue:
            wtr.write(read_val.Export())
        else:
            if self.multi_field_packstring:
                wtr.write(struct.pack(self.type_or_packstring, *read_val))
            else:
                wtr.write(struct.pack(self.type_or_packstring, read_val))
            

        if self.byte_padding:
            wtr.write(bytearray(self.byte_padding))

# These share the exact field names as the Creature type so that the CreatureDelta fields
# can easily be applied onto a Creature with `setattr` in the future, or generated by diffing two Creatures.
DELTA_TYPES = [
    MockType("position", LongVector3),
    MockType("orientation", FloatVector3),
    MockType("velocity", FloatVector3),
    MockType("acceleration", FloatVector3),
    MockType("retreat", FloatVector3),
    MockType("headRotation", '<f'),
    MockType("physicsFlags", '<I'),
    MockType("hostility", '<B'),
    MockType("creatureType", '<I'),
    MockType("mode", '<B'),
    MockType("modeTimer", '<i'),
    MockType("combo", '<i'),
    MockType("lastHitTime", '<i'),
    MockType("appearance", Appearance),
    MockType("creatureFlags", '<H'),
    MockType("rollTime", '<i'),
    MockType("stunTime", '<i'),
    MockType("slowedTime", '<i'),
    MockType("iceEffectTime", '<i'),
    MockType("windEffectTime", '<i'),
    MockType("showPatchTime", '<f'),
    MockType("classType", '<B'),
    MockType("specialization", '<B'),
    MockType("chargedMP", '<f'),
    MockType("unkIntVec1", IntVector3),
    MockType("unkIntVec2", IntVector3),
    MockType("rayHit", FloatVector3),
    MockType("HP", '<f'),
    MockType("MP", '<f'),
    MockType("blockPower", '<f'),
    MockType("statMultipliers", StatMultipliers),
    MockType("unkByte1", '<B'),
    MockType("unkByte2", '<B'),
    MockType("level", '<i'),
    MockType("XP", '<i'),
    MockType("parentOwner", '<q'),
    MockType("unkLong1", '<q'),
    MockType("powerBase", '<B'),
    MockType("unkInt1", '<i'),
    MockType("superWeird", IntVector3), # Spawn chunk, need to rename
    MockType("spawnPosition", LongVector3),
    MockType("unkIntVec3", IntVector3),
    MockType("unkByte3", '<B'),
    MockType("consumable", Item),
    MockType("equipment", Equipment),
    MockType("name", '16s'),
    MockType("skills", '<iiiiiiiiiii', multi_field_packstring=True),
    MockType("manaCubes", '<i')
]
assert(len(DELTA_TYPES) == 48)
    

class CreatureDelta():
    def __init__(self, entity_id, fields):
        self.entity_id = entity_id
        self.fields = fields

    @classmethod
    def Import(self, data):
        rdr = io.BytesIO(zlib.decompress(data))
        entity_id, = struct.unpack('<q', rdr.read(8))
        bitfield, = struct.unpack('<q', rdr.read(8))

        fields = {}
        for i in range(len(DELTA_TYPES)):
            t = DELTA_TYPES[i]
            if (1 << i) & bitfield:
                fields[t.field_name] = t.Read(rdr)

        # Special-case for name field
        if 'name' in fields:
            # c-string, split by first null and decode from bytes.
            fields['name'] = fields['name'].split(b'\x00')[0].decode()

        return CreatureDelta(entity_id, fields)

    def Export(self):
        # Special-case for name field
        if 'name' in self.fields:
            # Make sure it's encoded into a bytes-like object.
            self.fields['name'] = self.fields['name'].encode()

        bitfield = 0
        field_output = io.BytesIO()

        for i in range(len(DELTA_TYPES)):
            t = DELTA_TYPES[i]
            if t.field_name in self.fields:
                # Set the bit
                bitfield |= (1<<i)

                # Write the data
                t.Write(field_output, self.fields[t.field_name])


        output = struct.pack('<q', self.entity_id)
        output += struct.pack('<q', bitfield)
        output += field_output.getbuffer()

        return zlib.compress(output)
