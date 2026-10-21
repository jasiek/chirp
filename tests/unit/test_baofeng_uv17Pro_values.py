import os

from tests.unit import base  # noqa
from chirp import chirp_common
from chirp.drivers import baofeng_uv17Pro

IMAGES = os.path.join(os.path.dirname(__file__), "..", "images")
MODELS = (
    (baofeng_uv17Pro.UV5RMini, "Baofeng_UV-5R_Mini.img"),
    (baofeng_uv17Pro.UV5GMini, "Baofeng_UV-5G_Mini.img"),
)


def _settings(radio_cls, image):
    radio = radio_cls(os.path.join(IMAGES, image))
    radio.get_features()
    return radio, {setting.get_name(): setting
                   for setting in radio.get_settings().walk()}


def test_power_levels_match_manuals():
    watts = {
        baofeng_uv17Pro.UV5RMini: [5.0, 2.0],
        baofeng_uv17Pro.UV5GMini: [5.0, 0.5],
    }
    for radio_cls, image in MODELS:
        radio, _ = _settings(radio_cls, image)
        levels = radio.get_features().valid_power_levels

        assert [str(level) for level in levels] == ["High", "Low"]
        assert [chirp_common.dBm_to_watts(float(level))
                for level in levels] == watts[radio_cls]


def test_squelch_levels_match_manuals():
    levels = {
        baofeng_uv17Pro.UV5RMini: ["Off"] + list("12345"),
        baofeng_uv17Pro.UV5GMini: ["Off"] + list("123456789"),
    }
    for radio_cls, image in MODELS:
        _, settings = _settings(radio_cls, image)
        squelch = settings["settings.squelch"]

        assert squelch.value.get_options() == levels[radio_cls]
        assert str(squelch.value) == "3", radio_cls.MODEL


def test_labels_match_manual():
    for radio_cls, image in MODELS:
        _, settings = _settings(radio_cls, image)

        assert settings["settings.voice"].get_shortname() == "Language"
        assert settings["settings.sidetone"].value.get_options() == [
            "Off", "DT-ST", "ANI-ST", "DT+ANI"]
        assert settings["settings.powerondistype"].value.get_options() == [
            "Picture", "Voltage"]
