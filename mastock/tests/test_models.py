"""Tests pour les modèles API."""

import pytest
from mastock.api.models import (
    Climb, Hold, Face, Grade, ClimbSetter, ClimbHold, HoldType,
    parse_holds_list, FacePicture
)


class TestHoldType:
    def test_hold_types(self):
        assert HoldType.START.value == "S"
        assert HoldType.OTHER.value == "O"
        assert HoldType.FEET.value == "F"
        assert HoldType.TOP.value == "T"


class TestParseHoldsList:
    def test_parse_simple(self):
        holds = parse_holds_list("S829279 O828906 T829009")
        assert len(holds) == 3
        assert holds[0].hold_type == HoldType.START
        assert holds[0].hold_id == 829279
        assert holds[1].hold_type == HoldType.OTHER
        assert holds[2].hold_type == HoldType.TOP

    def test_parse_with_feet(self):
        holds = parse_holds_list("S829284 F829104 F829656 O829309 T829220")
        assert len(holds) == 5
        feet_holds = [h for h in holds if h.hold_type == HoldType.FEET]
        assert len(feet_holds) == 2

    def test_parse_multiple_starts(self):
        holds = parse_holds_list("S829279 S829528 O828906 T829009")
        starts = [h for h in holds if h.hold_type == HoldType.START]
        assert len(starts) == 2

    def test_parse_empty_string(self):
        holds = parse_holds_list("")
        assert holds == []

    def test_parse_none_string(self):
        holds = parse_holds_list(None)
        assert holds == []

    def test_parse_invalid_type_ignored(self):
        holds = parse_holds_list("S829279 X999999 T829009")
        assert len(holds) == 2  # X est ignoré


class TestHold:
    def test_centroid(self):
        hold = Hold(
            id=828902,
            area=2226.00,
            polygon_str="559.96,2358.89 536.00,2382.86",
            touch_polygon_str="",
            path_str="",
            centroid_str="572.53 2397.11"
        )
        x, y = hold.centroid
        assert x == pytest.approx(572.53)
        assert y == pytest.approx(2397.11)

    def test_get_polygon_points(self):
        hold = Hold(
            id=828902,
            area=2226.00,
            polygon_str="559.96,2358.89 536.00,2382.86 610.34,2408.98",
            touch_polygon_str="",
            path_str="",
            centroid_str="572.53 2397.11"
        )
        points = hold.get_polygon_points()
        assert len(points) == 3
        assert points[0] == pytest.approx((559.96, 2358.89), rel=0.01)

    def test_from_api(self):
        data = {
            "id": 828902,
            "area": "2226.00",
            "polygonStr": "559.96,2358.89 536.00,2382.86",
            "touchPolygonStr": "611.34,2537.10",
            "pathStr": "M559.96,2358.89L536.00,2382.86z",
            "centroidStr": "572.53 2397.11",
            "topPolygonStr": "552.37,2331.13"
        }
        hold = Hold.from_api(data)
        assert hold.id == 828902
        assert hold.area == 2226.00
        assert "559.96" in hold.polygon_str


class TestGrade:
    def test_grade_creation(self):
        grade = Grade(ircra=20.5, hueco="V6", font="7A", dankyu="1Q")
        assert grade.ircra == 20.5
        assert grade.font == "7A"


class TestClimb:
    def test_from_api_minimal(self):
        data = {
            "id": "test-id",
            "name": "Test Climb",
            "holdsList": "S829279 T829009",
            "feetRule": "Pieds des mains",
            "faceId": "face-id",
            "wallId": "wall-id",
            "wallName": "Test Wall",
            "dateCreated": "2025-12-17T10:56:38.491973-05:00"
        }
        climb = Climb.from_api(data)
        assert climb.id == "test-id"
        assert climb.name == "Test Climb"
        assert climb.feet_rule == "Pieds des mains"

    def test_from_api_with_grade(self):
        data = {
            "id": "test-id",
            "name": "Test Climb",
            "holdsList": "S829279 T829009",
            "feetRule": "",
            "faceId": "face-id",
            "wallId": "wall-id",
            "wallName": "Test Wall",
            "dateCreated": "",
            "crowdGrade": {
                "ircra": 20.5,
                "hueco": "V6",
                "font": "7A",
                "dankyu": "1Q"
            }
        }
        climb = Climb.from_api(data)
        assert climb.grade is not None
        assert climb.grade.font == "7A"

    def test_from_api_with_setter(self):
        data = {
            "id": "test-id",
            "name": "Test Climb",
            "holdsList": "S829279 T829009",
            "feetRule": "",
            "faceId": "face-id",
            "wallId": "wall-id",
            "wallName": "Test Wall",
            "dateCreated": "",
            "climbSetters": {
                "id": "setter-id",
                "fullName": "John Doe",
                "avatar": "avatar.jpg"
            }
        }
        climb = Climb.from_api(data)
        assert climb.setter is not None
        assert climb.setter.full_name == "John Doe"

    def test_get_holds(self):
        climb = Climb(
            id="test",
            name="Test",
            holds_list="S829279 O828906 T829009",
            feet_rule="",
            face_id="",
            wall_id="",
            wall_name="",
            date_created=""
        )
        holds = climb.get_holds()
        assert len(holds) == 3


class TestFace:
    def test_from_api_with_holds(self):
        data = {
            "id": "face-id",
            "gym": "Montoboard",
            "wall": "Stōkt board",
            "picture": {
                "name": "test.jpg",
                "width": 2263,
                "height": 3000
            },
            "feetRulesOptions": ["Tous pieds", "Pieds des mains"],
            "hasSymmetry": False,
            "totalClimbs": 1017,
            "holds": [
                {
                    "id": 828902,
                    "area": "2226.00",
                    "polygonStr": "559.96,2358.89",
                    "touchPolygonStr": "",
                    "pathStr": "",
                    "centroidStr": "572.53 2397.11"
                }
            ]
        }
        face = Face.from_api(data)
        assert face.id == "face-id"
        assert face.gym == "Montoboard"
        assert face.picture.width == 2263
        assert len(face.holds) == 1
        assert face.holds[0].id == 828902
