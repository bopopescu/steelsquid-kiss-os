#!/usr/bin/python -OO


'''
List and connect to wifi network using network manager

@organization: Steelsquid
@author: Andreas Nilsson
@contact: steelsquid@gmail.com
@license: GNU Lesser General Public License v2.1
@change: 2013-07-31 Created
'''


import sys
import dbus
import os
import steelsquid_utils
import shutil
import socket
import struct    


WIRELESS_CAPABILITIES_NONE = "none"
WIRELESS_CAPABILITIES_WEP = "wep"
WIRELESS_CAPABILITIES_WPA = "wpa"
WIRELESS_CAPABILITIES_UNKNOWN = "unknown"
NM_802_11_AP_SEC_PAIR_WEP40 = 0x1
NM_802_11_AP_SEC_PAIR_WEP104 = 0x2
NM_802_11_AP_SEC_GROUP_WEP40 = 0x10
NM_802_11_AP_SEC_GROUP_WEP104 = 0x20
NM_802_11_AP_SEC_KEY_MGMT_PSK = 0x100
NM_802_11_AP_SEC_KEY_MGMT_802_1X = 0x200
is_net_connected = False


def is_connected():
    '''
    Is network connected.
    @requires: True/False
    '''
    return is_net_connected


def get_access_points(returnWired=False):
    '''
    Get list of all available devices.
    @return: [[device, ssid, hw_address, wireless_capabilities (none, wep, wpa)]...]
    '''
    devices = []
    wired = None
    for device in NetworkManager.GetDevices():
        device_name = device.Udi[device.Udi.rfind('/') + 1:]
        try:
            specific_device = device.SpecificDevice()
            if device.DeviceType == NM_DEVICE_TYPE_ETHERNET:
                wired = [device_name, "Wired", specific_device.HwAddress, WIRELESS_CAPABILITIES_NONE, False]
            else:
                aps = specific_device.GetAccessPoints()
                for ap in aps:
                    try:
                        if ap.Flags == NM_802_11_AP_FLAGS_PRIVACY:
                            if ap.WpaFlags & NM_802_11_AP_SEC_KEY_MGMT_PSK | NM_802_11_AP_SEC_KEY_MGMT_802_1X:
                                devices.append([device_name, ap.Ssid, ap.HwAddress, WIRELESS_CAPABILITIES_WPA])
                            elif ap.WpaFlags & NM_802_11_AP_SEC_PAIR_WEP40 | NM_802_11_AP_SEC_PAIR_WEP104 | NM_802_11_AP_SEC_GROUP_WEP40 | NM_802_11_AP_SEC_GROUP_WEP104:
                                devices.append([device_name, ap.Ssid, ap.HwAddress, WIRELESS_CAPABILITIES_WEP])
                            else:
                                devices.append([device_name, ap.Ssid, ap.HwAddress, WIRELESS_CAPABILITIES_UNKNOWN])
                        else:
                            devices.append([device_name, ap.Ssid, ap.HwAddress, WIRELESS_CAPABILITIES_NONE])
                    except:
                        devices.append([device_name, ap.Ssid, ap.HwAddress, WIRELESS_CAPABILITIES_NONE])
        except:
            pass
    if not wired == None and returnWired:
        devices.insert(0, wired)
    return devices


def get_access_points_ssid_wireless_capabilities():
    '''
    Get list of all available devices in a pipe string.
    @return: ssid|wireless_capabilities (none, wep, wpa)|...
    '''
    new_devices = []
    devices = get_access_points()
    for device in devices:
        new_devices.append(device[1])
        new_devices.append(device[3])
    if len(new_devices) == 0:
        return None
    else:
        return new_devices


def get_connected_access_point_name():
    '''
    Get ssid of connected acces point.
    @return: ssid (None = no connection)
    '''
    has_wired = False
    for conn in NetworkManager.ActiveConnections:
        settings = conn.Connection.GetSettings()['connection']
        if "ethernet" in settings['type']:
            has_wired = True
        else:
            return settings['id']
    if has_wired:
        return "Wired"
    else:
        return None


def connect_to_wifi(ssid):
    '''
    Connect to open access point.
    @param ssid: The ssid of the connection
    '''
    import uuid
    if not NetworkManager.NetworkingEnabled:
        NetworkManager.Enable(True)
    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "wireless" in ctype:
            connection.Delete()

    new_connection = {
        '802-11-wireless': {'mode': 'infrastructure',
                             'ssid': ssid},
        'connection': {'id': ssid,
                        'type': '802-11-wireless',
                        'uuid': str(uuid.uuid4())},
        'ipv4': {'method': 'auto'},
        'ipv6': {'method': 'auto'}
    }
    Settings.AddConnection(new_connection)

    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "wireless" in ctype:
            devices = NetworkManager.GetDevices()
            for dev in devices:
                if dev.DeviceType == NM_DEVICE_TYPE_WIFI:
                    NetworkManager.ActivateConnection(connection, dev, "/")
                    break
            break


def connect_to_wifi_wpa(ssid, password):
    '''
    Connect to WPA access point.
    @param ssid: The ssid of the connection
    @param password: The password of the connection
    @raise ValueError: Password must be between 8 and 63 chars and only letters and numbers
    '''
    import uuid
    l = len(password)
    if l < 8 or l > 63:
        raise ValueError("Password must be a sequence of between 8 and 63 characters")
    if not NetworkManager.NetworkingEnabled:
        NetworkManager.Enable(True)
    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "wireless" in ctype:
            connection.Delete()

    new_connection = {
        '802-11-wireless': {'mode': 'infrastructure',
                             'security': '802-11-wireless-security',
                             'ssid': ssid},
        '802-11-wireless-security': {'key-mgmt': 'wpa-psk',
                                      'psk': password},
        'connection': {'id': ssid,
                        'type': '802-11-wireless',
                        'uuid': str(uuid.uuid4())},
        'ipv4': {'method': 'auto'},
        'ipv6': {'method': 'auto'}
    }
    Settings.AddConnection(new_connection)

    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "wireless" in ctype:
            devices = NetworkManager.GetDevices()
            for dev in devices:
                if dev.DeviceType == NM_DEVICE_TYPE_WIFI:
                    NetworkManager.ActivateConnection(connection, dev, "/")
                    break
            break


def connect_to_wifi_wep(ssid, password):
    '''
    Connect to WEP access point.
    @param ssid: The ssid of the connection
    @param password: The password of the connection
    @raise ValueError: Password must be between 10 and 63 chars and only letters and numbers
    '''
    import uuid
    l = len(password)
    if l < 10 or l > 63:
        raise ValueError("Password must be a sequence of between 10 and 63 characters")
    if not password.isalnum():
        raise ValueError("Password must be letters and numbers")
    if not NetworkManager.NetworkingEnabled:
        NetworkManager.Enable(True)
    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "wireless" in ctype:
            connection.Delete()

    new_connection = {
        '802-11-wireless': {'mode': 'infrastructure',
                             'security': '802-11-wireless-security',
                             'ssid': ssid},
        '802-11-wireless-security': {'auth-alg': 'open',
                                     'key-mgmt': 'none',
                                     'wep-key-type': '2',
                                     'wep-key0': password},
        'connection': {'id': ssid,
                        'type': '802-11-wireless',
                        'uuid': str(uuid.uuid4())},
        'ipv4': {'method': 'auto'},
        'ipv6': {'method': 'auto'}
    }
    Settings.AddConnection(new_connection)

    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "wireless" in ctype:
            devices = NetworkManager.GetDevices()
            for dev in devices:
                if dev.DeviceType == NM_DEVICE_TYPE_WIFI:
                    NetworkManager.ActivateConnection(connection, dev, "/")
                    break
            break


def on_network_connect():
    '''
    This will trigger on network connect.
    '''
    global is_net_connected
    if not is_net_connected:
        pass
    is_net_connected = True


def vpn_configured():
    '''
    Has setup vpn
    Return: The name of the vpn
    None if not configured
    '''
    import uuid
    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "vpn" in ctype:
            cname = connection.GetSettings()['connection']['id']
            return cname
    return None


def vpn_openvpn(ovpn_file, username, password):
    '''
    Setup openvpn connection.
    @param ovpn_file: The ovpn file
    @param username: The username
    @param password: The password
    '''
    import uuid
    connections = Settings.ListConnections()
    for connection in connections:
        ctype = connection.GetSettings()['connection']['type']
        if "vpn" in ctype:
            connection.Delete()
    base_folder = steelsquid_utils.STEELSQUID_FOLDER + "/vpn/"
    file_folder = os.path.dirname(ovpn_file) + "/"
    if file_folder=="/":
        file_folder = "./"    
    steelsquid_utils.make_dirs(base_folder)
    name = None
    remote = None
    port = None
    reneg_sec = None
    ca = None
    tls_auth = None
    ta_dir = None
    comp_lzo = "no"
    cipher = None
    with open(ovpn_file) as fp:
        for line in fp:
            line = line.replace('\r', '')  
            line = line.replace('\n', '')  
            sline = line.split(' ')
            if name == None:
                name = line
            elif sline[0] == 'remote':
                remote = sline[1]
                port = sline[2]
            elif sline[0] == 'reneg-sec':
                reneg_sec = sline[1]
            elif sline[0] == 'ca':
                ca = sline[1]
            elif sline[0] == 'tls-auth':
                tls_auth = sline[1]
                if len(sline)==3:
                    ta_dir = sline[2]
            elif sline[0] == 'comp-lzo':
                comp_lzo = "yes"
            elif sline[0] == 'cipher':
                cipher = sline[1]
    if ca != None:
        try:
            os.remove(base_folder + ca)
        except:
            pass
        shutil.copy2(file_folder + ca, base_folder + ca)
    if tls_auth != None:
        try:
            os.remove(base_folder + tls_auth)
        except:
            pass
        shutil.copy2(file_folder + tls_auth, base_folder + tls_auth)
    new_connection = {
        'connection': {'id': name,
                       'type': 'vpn',
                       'uuid': str(uuid.uuid4())},
        'ipv4': {'method': 'auto'},
        'vpn': {'data': {'ca': base_folder + ca,
                'comp-lzo': comp_lzo,
                'connection-type': 'password',
                'password-flags': '0',
                'port': port,
                'remote': remote,
                'reneg-seconds': reneg_sec,
                'ta': base_folder + tls_auth,
                'ta-dir': ta_dir,
                'username': username},
          'secrets': {'password': password},
          'service-type': 'org.freedesktop.NetworkManager.openvpn'}
    }
    Settings.AddConnection(new_connection)


def vpn_connected():
    '''
    Is connected to vpn
    '''
    for conn in NetworkManager.ActiveConnections:
        if conn.Vpn:
            return True
    return False


def vpn_connect():
    '''
    Connect vpn.
    If no vpn is configured you must firt execute setup_openvpn
    '''
    if not NetworkManager.NetworkingEnabled:
        NetworkManager.Enable(True)
    for conn in NetworkManager.ActiveConnections:
        if conn.Vpn:
            raise Exception("Vpn is already active")

    devices = NetworkManager.GetDevices()
    the_dev = None
    for dev in devices:
        if dev.DeviceType == NM_DEVICE_TYPE_WIFI or dev.DeviceType == NM_DEVICE_TYPE_ETHERNET:
            the_dev = dev
            break
    if the_dev != None:
        connections = Settings.ListConnections()
        for connection in connections:
            ctype = connection.GetSettings()['connection']['type']
            if "vpn" in ctype:
                NetworkManager.ActivateConnection(connection, the_dev, "/")
                break
    else:
        raise Exception("No active, managed device found")


def vpn_disconnect():
    '''
    disconnect from vpn
    '''
    for conn in NetworkManager.ActiveConnections:
        if conn.Vpn:
            NetworkManager.DeactivateConnection(conn)


def print_help():
    '''
    Print help to the screen
    '''
    from steelsquid_utils import printb
    print("")
    printb("DESCRIPTION")
    print("List and connect to wifi network.")
    print("Also import/connect to openvpn.")
    print("")
    printb("net status")
    print("See which access point you are connected to")
    print("Will also print your ip-number.")
    print("")
    printb("net list")
    print("List all wifi network access points")
    print("")
    printb("net connect <number>")
    print("Connect to open wifi network.")
    print("")
    printb("net connect <number> <password>")
    print("Connect to protected wifi network.")
    print("")
    printb("net vpn-openvpn <ovpn_file> <username> <password>")
    print("Import a .ovpn file (configure vpn)")
    print("")
    printb("net vpn-status")
    print("Unconfigured, Configured: <name of vpn>, Connected: <name of vpn>")
    print("")
    printb("net vpn-connect")
    print("Connect to vpn")
    print("")
    printb("net vpn-disconnect")
    print("Disconnect from vpn")
    print("\n")


def main():
    '''
    The main function
    '''
    try:
        if len(sys.argv) < 2:
            print_help()
        elif sys.argv[1] == "list":
            acc_p_list = get_access_points(False)
            nummer = 1
            print("\n\033[1m   Security   Name\033[0m")
            for acc_p in acc_p_list:
                if acc_p[3] == WIRELESS_CAPABILITIES_NONE:
                    print("\033[1m" + str(nummer) + "\033[0m  Open       " + acc_p[1])
                else:
                    print("\033[1m" + str(nummer) + "\033[0m  Protected  " + acc_p[1])
                nummer = nummer + 1
            print("")
        elif sys.argv[1] == "system-list":
            acc_p_list = get_access_points(False)
            for acc_p in acc_p_list:
                print(acc_p[3] + "|" + acc_p[1])
            sys.stdout.flush()
        elif sys.argv[1] == "connect":
            if os.getuid() != 0:
                print "This program requires root privileges.  Run as root using 'sudo'."
            else:
                acc_p_list = get_access_points(False)
                if len(sys.argv) == 3:
                    acc_p = acc_p_list[int(sys.argv[2]) - 1]
                    acc_ssid = acc_p[1]
                    connect_to_wifi(acc_ssid)
                elif len(sys.argv) == 4:
                    acc_p = acc_p_list[int(sys.argv[2]) - 1]
                    acc_t = acc_p[3]
                    acc_ssid = acc_p[1]
                    if acc_t == WIRELESS_CAPABILITIES_WPA:
                        connect_to_wifi_wpa(acc_ssid, sys.argv[3])
                    elif acc_t == WIRELESS_CAPABILITIES_WEP:
                        connect_to_wifi_wep(acc_ssid, sys.argv[3])
                else:
                    print_help()
        elif sys.argv[1] == "system-connect":
            steelsquid_utilsshout( "###dfgdfgdfg")
            acc_p_list = get_access_points(False)
            if len(sys.argv) == 3:
                steelsquid_utilsshout( "###dfgdfgdfgsssss")
                connect_to_wifi(sys.argv[2])
            else:
                connected = False
                for acc_p in acc_p_list:
                    if acc_p[1] == sys.argv[2]:
                        acc_t = acc_p[3]
                        steelsquid_utilsshout( "###"+sys.argv[2]+":"+sys.argv[3])
                        if acc_t == WIRELESS_CAPABILITIES_WPA:
                            steelsquid_utilsshout("kjjlkjlkjlkjl")
                            connect_to_wifi_wpa(sys.argv[2], sys.argv[3])
                            connected = True
                        elif acc_t == WIRELESS_CAPABILITIES_WEP:
                            connect_to_wifi_wep(sys.argv[2], sys.argv[3])
                            connected = True
                sys.stdout.flush()
                if not connected:
                    print "SSID not found"
                    sys.stdout.flush()
                    os._exit(9)
        elif sys.argv[1] == "status":
            if os.getuid() != 0:
                print "This program requires root privileges.  Run as root using 'sudo'."
            else:
                name = get_connected_access_point_name()
                if name == None:
                    print("\nConnected to network: \033[1mNot connected!\033[0m\n")
                else:
                    print("\nConnected to network: \033[1m" + name + "\033[0m")
                    print("Network Wired IP: \033[1m" + steelsquid_utils.network_ip_wired() + "\033[0m")
                    print("Network Wifi IP: \033[1m" + steelsquid_utils.network_ip_wifi() + "\033[0m")
                    print("Internet IP: \033[1m" + steelsquid_utils.network_ip_wan() + "\033[0m\n")
        elif sys.argv[1] == "system-status":
            name = get_connected_access_point_name()
            if name == None:
                print("None")
            else:
                print(name)
            sys.stdout.flush()
        elif sys.argv[1] == "vpn-openvpn":
            vpn_openvpn(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == "vpn-status":
            name = vpn_configured()
            if name != None:
                if vpn_connected():
                    print "Connected: " + name
                else:
                    print "Configured: " + name
            else:
                print "Unconfigured"
        elif sys.argv[1] == "vpn-connect":
            vpn_connect()
        elif sys.argv[1] == "vpn-disconnect":
            vpn_disconnect()            
        else:
            print_help()
        os._exit(0)
    except Exception as e:
        print e
        sys.stdout.flush()
        os._exit(9)


PY3 = sys.version_info >= (3, 0)
if PY3:
    basestring = str
    unicode = str
elif not hasattr(__builtins__, 'bytes'):
    bytes = lambda x, y=None: chr(x[0]) if x else x

try:
    debuglevel = int(os.environ['NM_DEBUG'])
    
    def debug(msg, data):
        sys.stderr.write(msg + "\n")
        sys.stderr.write(repr(data) + "\n")
except:
    debug = lambda *args: None


class NMDbusInterface(object):
    bus = dbus.SystemBus()
    dbus_service = 'org.freedesktop.NetworkManager'
    object_path = None

    def __init__(self, object_path=None):
        if isinstance(object_path, NMDbusInterface):
            object_path = object_path.object_path
        self.object_path = self.object_path or object_path
        self.proxy = self.bus.get_object(self.dbus_service, self.object_path)
        self.interface = dbus.Interface(self.proxy, self.interface_name)

        properties = []
        try:
            properties = self.proxy.GetAll(self.interface_name,
                                           dbus_interface='org.freedesktop.DBus.Properties')
        except dbus.exceptions.DBusException as e:
            if e.get_dbus_name() != 'org.freedesktop.DBus.Error.UnknownMethod':
                raise
        for p in properties:
            p = str(p)
            if not hasattr(self.__class__, p):
                setattr(self.__class__, p, self._make_property(p))

    def _make_property(self, name):
        def get(self):
            data = self.proxy.Get(self.interface_name, name, dbus_interface='org.freedesktop.DBus.Properties')
            debug("Received property %s.%s" % (self.interface_name, name), data)
            return self.postprocess(name, self.unwrap(data))

        def set(self, value):
            #data = self.wrap(self.preprocess(name, data))
            debug("Setting property %s.%s" % (self.interface_name, name), value)
            return self.proxy.Set(self.interface_name, name, value, dbus_interface='org.freedesktop.DBus.Properties')
        return property(get, set)

    def unwrap(self, val):
        if isinstance(val, dbus.ByteArray):
            return "".join([str(x) for x in val])
        if isinstance(val, (dbus.Array, list, tuple)):
            return [self.unwrap(x) for x in val]
        if isinstance(val, (dbus.Dictionary, dict)):
            return dict([(self.unwrap(x), self.unwrap(y)) for x, y in val.items()])
        if isinstance(val, dbus.ObjectPath):
            if val.startswith('/org/freedesktop/NetworkManager/'):
                classname = val.split('/')[4]
                classname = {
                   'Settings': 'Connection',
                   'Devices': 'Device',
                }.get(classname, classname)
                return globals()[classname](val)
        if isinstance(val, (dbus.Signature, dbus.String)):
            return unicode(val)
        if isinstance(val, dbus.Boolean):
            return bool(val)
        if isinstance(val, (dbus.Int16, dbus.UInt16, dbus.Int32, dbus.UInt32, dbus.Int64, dbus.UInt64)):
            return int(val)
        if isinstance(val, dbus.Byte):
            return bytes([int(val)])
        return val

    def wrap(self, val):
        if isinstance(val, NMDbusInterface):
            return val.object_path
        if hasattr(val, 'mro'):
            for klass in val.mro():
                if klass.__module__ == '_dbus_bindings':
                    return val
        if hasattr(val, '__iter__') and not isinstance(val, basestring):
            if hasattr(val, 'items'):
                return dict([(x, self.wrap(y)) for x, y in val.items()])
            else:
                return [self.wrap(x) for x in val]
        return val

    def  __getattr__(self, name):
        try:
            return super(NMDbusInterface, self).__getattribute__(name)
        except AttributeError:
            return self.make_proxy_call(name)

    def make_proxy_call(self, name):
        def proxy_call(*args, **kwargs):
            func = getattr(self.interface, name)
            args, kwargs = self.preprocess(name, args, kwargs)
            args = self.wrap(args)
            kwargs = self.wrap(kwargs)
            debug("Calling function %s.%s" % (self.interface_name, name), (args, kwargs))
            ret = func(*args, **kwargs)
            debug("Received return value for %s.%s" % (self.interface_name, name), ret)
            return self.postprocess(name, self.unwrap(ret))
        return proxy_call

    def connect_to_signal(self, signal, handler, *args, **kwargs):
        def helper(*args, **kwargs):
            args = [self.unwrap(x) for x in args]
            handler(*args, **kwargs)
        args = self.wrap(args)
        kwargs = self.wrap(kwargs)
        return self.proxy.connect_to_signal(signal, helper, *args, **kwargs)

    def postprocess(self, name, val):
        return val

    def preprocess(self, name, args, kwargs):
        return args, kwargs


class NetworkManager(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager'
    object_path = '/org/freedesktop/NetworkManager'

    def preprocess(self, name, args, kwargs):
        if name in ('AddConnection', 'Update', 'AddAndActivateConnection'):
            settings = args[0]
            for key in settings:
                if 'mac-address' in settings[key]:
                    settings[key]['mac-address'] = fixups.mac_to_dbus(settings[key]['mac-address'])
                if 'bssid' in settings[key]:
                    settings[key]['bssid'] = fixups.mac_to_dbus(settings[key]['mac-address'])
            if 'ssid' in settings.get('802-11-wireless', {}):
                settings['802-11-wireless']['ssid'] = fixups.ssid_to_dbus(settings['802-11-wireless']['ssid'])
            if 'ipv4' in settings:
                if 'addresses' in settings['ipv4']:
                    settings['ipv4']['addresses'] = [fixups.addrconf_to_dbus(addr) for addr in settings['ipv4']['addresses']]
                if 'routes' in settings['ipv4']:
                    settings['ipv4']['routes'] = [fixups.route_to_dbus(route) for route in settings['ipv4']['routes']]
                if 'dns' in settings['ipv4']:
                    settings['ipv4']['dns'] = [fixups.addr_to_dbus(addr) for addr in settings['ipv4']['dns']]
        return args, kwargs
NetworkManager = NetworkManager()


class Settings(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.Settings'
    object_path = '/org/freedesktop/NetworkManager/Settings'
    preprocess = NetworkManager.preprocess
Settings = Settings()


class Connection(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.Settings.Connection'
    has_secrets = ['802-1x', '802-11-wireless-security', 'cdma', 'gsm', 'pppoe', 'vpn']

    def GetSecrets(self, name=None):
        if name == None:
            settings = self.GetSettings()
            for key in self.has_secrets:
                if key in settings:
                    name = key
                    break
            else:
                return {}
        return self.make_proxy_call('GetSecrets')(name)

    def postprocess(self, name, val):
        if name == 'GetSettings':
            if 'ssid' in val.get('802-11-wireless', {}):
                val['802-11-wireless']['ssid'] = fixups.ssid_to_python(val['802-11-wireless']['ssid'])
            for key in val:
                val_ = val[key]
                if 'mac-address' in val_:
                    val_['mac-address'] = fixups.mac_to_python(val_['mac-address'])
                if 'bssid' in val_:
                    val_['bssid'] = fixups.mac_to_python(val_['bssid'])
            if 'ipv4' in val:
                val['ipv4']['addresses'] = [fixups.addrconf_to_python(addr) for addr in val['ipv4']['addresses']]
                val['ipv4']['routes'] = [fixups.route_to_python(route) for route in val['ipv4']['routes']]
                val['ipv4']['dns'] = [fixups.addr_to_python(addr) for addr in val['ipv4']['dns']]
        return val
    preprocess = NetworkManager.preprocess


class ActiveConnection(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.Connection.Active'


class Device(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.Device'

    def SpecificDevice(self):
        return {
            NM_DEVICE_TYPE_ETHERNET: Wired,
            NM_DEVICE_TYPE_WIFI: Wireless,
        }[self.DeviceType](self.object_path)


class AccessPoint(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.AccessPoint'

    def postprocess(self, name, val):
        if name == 'Ssid':
            return fixups.ssid_to_python(val)
        return val


class Wired(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.Device.Wired'


class Wireless(NMDbusInterface):
    interface_name = 'org.freedesktop.NetworkManager.Device.Wireless'






def const(prefix, val):
    prefix = 'NM_' + prefix.upper() + '_'
    for key, vval in globals().items():
        if 'REASON' in key and 'REASON' not in prefix:
            continue
        if key.startswith(prefix) and val == vval:
            return key.replace(prefix, '').lower()
    raise ValueError("No constant found for %s* with value %d", (prefix, val))


# Several fixer methods to make the data easier to handle in python
# - SSID sent/returned as bytes (only encoding tried is utf-8)
# - IP, Mac address and route metric encoding/decoding
class fixups(object):
    import socket    
    import struct    
    @staticmethod
    def ssid_to_python(ssid):
        count = 0
        try:
            for ch in ssid:
                ssid[count] = int(ch.replace("[", "").replace("]", ""))
                count = count + 1
            return "".join(map(chr, ssid))
        except:
            return "".join(ssid)

    @staticmethod
    def ssid_to_dbus(ssid):
        if isinstance(ssid, unicode):
            ssid = ssid.encode('utf-8')
        return [dbus.Byte(x) for x in ssid]

    @staticmethod
    def mac_to_python(mac):
        count = 0
        try:
            for ch in mac:
                mac[count] = int(ch.replace("[", "").replace("]", ""))
                count = count + 1
            return ":".join([("%02X" % int(value)) for value in mac])
        except:
            return "%02X:%02X:%02X:%02X:%02X:%02X" % tuple([ord(x) for x in mac])
            

    @staticmethod
    def mac_to_dbus(mac):
        return [dbus.Byte(int(x, 16)) for x in mac.split(':')]

    @staticmethod
    def addrconf_to_python(addrconf):
        addr, netmask, gateway = addrconf
        return [
            fixups.addr_to_python(addr),
            netmask,
            fixups.addr_to_python(gateway)
        ]

    @staticmethod
    def addrconf_to_dbus(addrconf):
        addr, netmask, gateway = addrconf
        return [
            fixups.addr_to_dbus(addr),
            netmask,
            fixups.addr_to_dbus(gateway)
        ]

    @staticmethod
    def addr_to_python(addr):
        return socket.inet_ntoa(struct.pack('I', addr))

    @staticmethod
    def addr_to_dbus(addr):
        return struct.unpack('I', socket.inet_aton(addr))

    @staticmethod
    def route_to_python(route):
        addr, netmask, gateway, metric = route
        return [
            fixups.addr_to_python(addr),
            netmask,
            fixups.addr_to_python(gateway),
            socket.ntohl(metric)
        ]

    @staticmethod
    def route_to_dbus(route):
        addr, netmask, gateway, metric = route
        return [
            fixups.addr_to_dbus(addr),
            netmask,
            fixups.addr_to_dbus(gateway),
            socket.htonl(metric)
        ]

# Constants below are generated with makeconstants.py. Do not edit manually.

NM_DEVICE_TYPE_UNKNOWN = 0
NM_DEVICE_TYPE_ETHERNET = 1
NM_DEVICE_TYPE_WIFI = 2
NM_802_11_AP_FLAGS_NONE = 0
NM_802_11_AP_FLAGS_PRIVACY = 1

c = const

if __name__ == '__main__':
    main()
