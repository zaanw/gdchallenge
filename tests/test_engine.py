import json
import math
import tempfile
import unittest
import zipfile
from pathlib import Path
from src.core.level import Level, Sample
from src.core.objects import Object
from src.core.serialization import encode_raw,decode_raw,read_gmd,export_gmd,convert
from src.core.validation import swept_hit,validate
from src.core.triggers import alpha,move,pulse,color,toggle
from src.generator import build,generate


class ObjectTests(unittest.TestCase):
    def test_transform_and_groups_roundtrip(self):
        level=Level(objects=[Object(1,12.345,-8,rotation=45,scale=.5,groups=(3,9))])
        _,objects=decode_raw(encode_raw(level))
        self.assertEqual(objects[0].groups,(3,9))
        self.assertEqual(objects[0].rotation,45)
        self.assertEqual(objects[0].scale,.5)
        self.assertAlmostEqual(objects[0].x,12.345)
        b=objects[0].bounds()
        self.assertAlmostEqual(b[2]-b[0],15*math.sqrt(2))

    def test_unknown_id(self):
        with self.assertRaises(ValueError): Object(999999,0,0).validate()

    def test_bad_parameters(self):
        for obj in [Object(1,float('nan'),0),Object(1,0,0,scale=0),
                    Object(1,0,0,groups=(0,)),Object(1,0,0,groups=(2,2)),
                    Object(1,0,0,channel=0),Object(1,0,0,properties={9999:1}),
                    Object(1,0,0,properties={6:5}),Object(1,0,0,properties={7:256}),
                    Object(1,0,0,properties={5:2}),Object(1,0,0,properties={10:'x'}),
                    Object(1,0,0,properties={51:2.5}),Object(1,0,0,properties={10:-1}),
                    Object(1007,0,0,properties={51:1,35:1.1})]:
            with self.subTest(obj=obj),self.assertRaises(ValueError): obj.validate()

    def test_triggers_encode(self):
        for obj in [alpha(10,3,.5),move(10,3),pulse(10),color(10,1,(255,0,0)),toggle(10,3,True)]:
            obj.validate()
            self.assertIn(1,obj.fields())


class GeometryTests(unittest.TestCase):
    def test_swept_collision_prevents_tunneling(self):
        a=Sample(0,0,0,1,'wave',True)
        b=Sample(1,100,0,1,'wave',True)
        self.assertTrue(swept_hit(a,b,(49,-1,51,1),1))
        self.assertFalse(swept_hit(a,b,(49,3,51,4),1))
        self.assertTrue(swept_hit(a,b,(49,1,51,2),1))

    def test_mutated_obstacle_is_detected(self):
        level=build()
        a=level.trajectory[4000]
        level.add(Object(1,a.x,a.y))
        report=validate(level)
        self.assertEqual(report['status'],'FAIL')
        self.assertTrue(report['contacts'])

    def test_dangling_group_and_channel(self):
        level=build()
        level.add(alpha(100,999,.1))
        level.add(pulse(100,999))
        errors=' '.join(validate(level)['errors'])
        self.assertIn('Dangling group',errors)
        self.assertIn('Dangling color',errors)

    def test_moving_solid_rejected(self):
        level=build()
        level.objects[0].groups=(333,)
        level.add(move(100,333))
        self.assertTrue(any('Moving solid' in e for e in validate(level)['errors']))

    def test_obstacle_overlaps_detected(self):
        level=build()
        level.add(Object(1,200,600))
        level.add(Object(1,201,600))
        self.assertGreater(validate(level)['obstacle_envelope_overlaps'],0)

    def test_portal_transition_corruption(self):
        level=build()
        next(o for o in level.objects if o.id==660).y+=100
        self.assertTrue(any('transition' in e for e in validate(level)['errors']))

    def test_ground_crossing(self):
        level=build()
        level.trajectory[0].y=-20
        self.assertTrue(any('ground' in e for e in validate(level)['errors']))

    def test_all_sections_and_modeled_wave_slopes(self):
        level=build()
        self.assertEqual(len(level.sections),7)
        self.assertEqual(level.sections[-1].end,44)
        for a,b in zip(level.trajectory,level.trajectory[1:]):
            if a.mode==b.mode=='wave' and level.section_at(a.t) is level.section_at(b.t):
                expected=2 if level.section_at(a.t).mini else 1
                self.assertAlmostEqual(abs((b.y-a.y)/(b.x-a.x)),expected,places=6)


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=tempfile.TemporaryDirectory()
        cls.output=Path(cls.directory.name)
        cls.report=generate(cls.output)

    @classmethod
    def tearDownClass(cls): cls.directory.cleanup()

    def test_release_validation(self):
        self.assertEqual(self.report['status'],'PASS_CONSERVATIVE_MODEL')
        self.assertEqual(self.report['errors'],[])
        self.assertEqual(self.report['samples'],10561)
        self.assertEqual(self.report['obstacle_envelope_overlaps'],0)
        self.assertTrue(all(t['geometry_continuous'] for t in self.report['transitions']))
        self.assertFalse(self.report['exact_gd_physics_verified'])

    def test_gmd_roundtrip(self):
        fields,raw=read_gmd(self.output/'ABSOLUTE_COLLAPSE.gmd')
        self.assertEqual(fields['k2'],'ABSOLUTE COLLAPSE')
        self.assertEqual(raw,(self.output/'ABSOLUTE_COLLAPSE.level').read_text())
        self.assertEqual(len(decode_raw(raw)[1]),self.report['objects'])
        self.assertTrue((self.output/'ABSOLUTE_COLLAPSE.gmd').read_bytes().startswith(b'<?xml'))
        # Independent importer-style extraction: k4 must itself contain objects.
        import xml.etree.ElementTree as ET
        entries=list(ET.parse(self.output/'ABSOLUTE_COLLAPSE.gmd').getroot().find('dict/dict'))
        k4=next(entries[i+1].text for i in range(0,len(entries),2) if entries[i].text=='k4')
        self.assertTrue(k4.startswith('kA2,'))
        self.assertEqual(len(k4.split(';')[1:-1]),self.report['objects'])
        self.assertTrue(all(part.startswith('1,') for part in k4.split(';')[1:-1]))

    def test_zip_integrity_and_actual_members(self):
        with zipfile.ZipFile(self.output/'ABSOLUTE_COLLAPSE.zip') as z:
            self.assertIsNone(z.testzip())
            for name in ['ABSOLUTE_COLLAPSE.gmd','validation_report.txt','import_instructions.md','trajectory.csv','README.md']:
                self.assertGreater(len(z.read(name)),0)
            self.assertEqual(z.read('ABSOLUTE_COLLAPSE.gmd'),(self.output/'ABSOLUTE_COLLAPSE.gmd').read_bytes())

    def test_converter_preserves_custom_header(self):
        with tempfile.TemporaryDirectory() as directory:
            raw=(self.output/'ABSOLUTE_COLLAPSE.level').read_text().replace('kA4,4','kA4,2')
            source=Path(directory)/'custom.level'
            target=Path(directory)/'custom.gmd'
            source.write_text(raw)
            convert(source,target)
            self.assertEqual(read_gmd(target)[1],raw)

    def test_deterministic_regeneration(self):
        before=(self.output/'ABSOLUTE_COLLAPSE.zip').read_bytes()
        generate(self.output)
        self.assertEqual(before,(self.output/'ABSOLUTE_COLLAPSE.zip').read_bytes())

    def test_corrupt_payload_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'bad.gmd'
            data=(self.output/'ABSOLUTE_COLLAPSE.gmd').read_bytes().replace(b'kA2,0',b'BROKEN',1)
            target.write_bytes(data)
            with self.assertRaises((ValueError,OSError,EOFError)): read_gmd(target)

    def test_bad_object_stream_rejected(self):
        for raw in ['kA4,4;1,1,2;', 'kA4,4;1,1,1,8,2,1,3,2;', 'kA4,4;1,999999,2,1,3,2;', 'kA4,4']:
            with self.subTest(raw=raw),self.assertRaises(ValueError): decode_raw(raw)


if __name__=='__main__': unittest.main()
