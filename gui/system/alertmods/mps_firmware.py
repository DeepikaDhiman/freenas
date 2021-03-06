from collections import defaultdict
import sysctl

from django.utils.translation import ugettext as _

from freenasUI.system.alert import alertPlugins, Alert, BaseAlert


class MPSFirmwareAlert(BaseAlert):

    def run(self):
        alerts = []
        mps = defaultdict(dict)
        for o in sysctl.filter('dev.mps'):
            mibs = o.name.split('.', 3)
            if len(mibs) < 4:
                continue

            number, mib = mibs[2:4]

            try:
                major = int(o.value.split('.', 1)[0])
                mps[number][mib] = major
            except:
                continue

        for number, mibs in mps.items():
            firmware = mibs.get('firmware_version')
            driver = mibs.get('driver_version')
            try:
                if int(firmware) != int(driver):
                    alerts.append(Alert(
                        Alert.WARN,
                        _(
                            'Firmware version %(fwversion)s does not match driver '
                            'version %(drversion)s for /dev/mps%(mps)s. Please '
                            'flash controller to P%(drversion)s IT firmware.'
                        ) % {
                            'fwversion': firmware,
                            'drversion': driver,
                            'mps': number,
                        }
                    ))
            except ValueError:
                # cast returned cthulu
                # This shouldn't ever happen but as a fallback try the old method
                if firmware != driver:
                    alerts.append(Alert(
                        Alert.WARN,
                        _(
                            'Firmware version %(fwversion)s does not match driver '
                            'version %(drversion)s for /dev/mps%(mps)s'
                        ) % {
                            'fwversion': firmware,
                            'drversion': driver,
                            'mps': number,
                        }
                    ))

        return alerts

alertPlugins.register(MPSFirmwareAlert)
