#!/usr/bin/env python

# Autoflash automatically formats any USB drive that you insert while it is running, and then copies 
# a set of files to it. Then it remounts the drive read-only and verifies the files against the originals.

# Usage: 

# 1. Put all the files you want to bulk copy into a folder and run 'md5sum * > manifest'
# 2. Run 'autoflash.py /path/to/folder/ LABEL'
# 3. Insert a USB flash drive.

# Flash drive will be formatted and the volume label set to LABEL. Then the files from manifest 
# are copied.

import dbus
import gobject
import sys
import hashlib
import time
import os

props = ['NativePath','DeviceFile','DeviceIsPartition','DeviceIsPartitionTable','DeviceIsReadOnly'
,'DeviceIsMounted','DeviceMountPaths','DeviceSize','DeviceBlockSize','PartitionTableCount'
,'DriveVendor','DriveModel','DriveRevision','DriveSerial','DriveConnectionInterface']


class Manifester(object):
    def __init__(self, path):
        self.path = path
        print 'Reading manifest from', self.path
        manifest = file(self.path+'/manifest')
        self.files = {}
        for line in manifest:
            line = line.strip()
            md5 = line[:32]
            name = line[34:]
            print md5, name
            d = file(path + '/' + name, 'rb').read()
            h = hashlib.md5(d).hexdigest()
            if h != md5:
                raise 'Source files do not match manifest.'
            self.files[name] = (d, md5)
        print 'Done.'

    def verify(self, path=None):
        if path is None:
            path = self.path
        print 'Verifying', path
        for name, (d, md5) in self.files.iteritems():
            print path + '/' + name
            d1 = file(path + '/' + name, 'rb').read()
            
            h = hashlib.md5(d1).hexdigest()
            if (h != md5) or (d != d1):
                print md5, h
                print 'd', d, 'd1', d1
                raise 'Destination files do not match source.'

    def copy(self, path):
        print 'Copying files...'
        print 'Copying', path
        for name, (d, md5) in self.files.iteritems():
            print path + '/' + name
            o = file(path + '/' + name, 'wb')
            o.write(d)
            o.flush()
            os.fsync(o.fileno())
            o.close()


class DeviceAddedListener:
    def __init__(self, manifester):

        self.manifester = manifester

        self.bus = dbus.SystemBus()
        self.ud_manager_obj = self.bus.get_object("org.freedesktop.UDisks", 
                                                   "/org/freedesktop/UDisks")

        self.ud_manager = dbus.Interface(self.ud_manager_obj,
                                          "org.freedesktop.UDisks")

        self.ud_manager.connect_to_signal("DeviceAdded", self._filter)

    def _filter(self, dev):
        device_obj = self.bus.get_object("org.freedesktop.UDisks", dev)
        device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
        usb = device_props.Get('org.freedesktop.UDisks.Device', 'DriveConnectionInterface')
        part = device_props.Get('org.freedesktop.UDisks.Device', 'DeviceIsPartition')
        if part and usb == 'usb':
            try:
                self._handle(dev)
            except dbus.exceptions.DBusException, e:
                print e
                print 'Failure'
            #except:
            #    print 'Failure'
            else:
                print 'Success'

    def _handle(self, dev):
        device_obj = self.bus.get_object("org.freedesktop.UDisks", dev)
        device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
        print 'Got device, waiting for OS to mount it.'
        while not device_props.Get('org.freedesktop.UDisks.Device', 'DeviceIsMounted'):
            time.sleep(0.5)
        device_obj.FilesystemUnmount([], dbus_interface='org.freedesktop.UDisks.Device')
        print 'Unmounted OK'
        device_obj.FilesystemCreate('vfat', ['label=%s' % sys.argv[2]], dbus_interface='org.freedesktop.UDisks.Device')
        print 'Formatted as vfat'
        device_obj.FilesystemMount('', [], dbus_interface='org.freedesktop.UDisks.Device')
        paths = device_props.Get('org.freedesktop.UDisks.Device', 'DeviceMountPaths')
        self.manifester.copy(paths[0])
        device_obj.FilesystemUnmount([], dbus_interface='org.freedesktop.UDisks.Device')
        device_obj.FilesystemMount('', ['ro'], dbus_interface='org.freedesktop.UDisks.Device')
        self.manifester.verify(paths[0])
        device_obj.FilesystemUnmount([], dbus_interface='org.freedesktop.UDisks.Device')
        
if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    m = Manifester(sys.argv[1])
    DeviceAddedListener(m)
    loop.run()

