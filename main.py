import dbus
import gobject


props = ['NativePath'
,'DeviceDetectionTime'
,'DeviceMediaDetectionTime'
,'DeviceMajor'
,'DeviceMinor'
,'DeviceFile'
,'DeviceFilePresentation'
#,'DeviceFileById'
#,'DeviceFileByPath'
#,'DeviceIsSystemInternal'
,'DeviceIsPartition'
,'DeviceIsPartitionTable'
#,'DeviceIsRemovable'
,'DeviceIsReadOnly'
#,'DeviceIsDrive'
#,'DeviceIsOpticalDisc'
,'DeviceIsMounted'
#,'DeviceMountPaths'
#,'DeviceMountedByUid'
,'DeviceSize'
,'DeviceBlockSize'
,'IdUsage'
,'IdType'
,'IdVersion'
,'IdUuid'
,'IdLabel'
,'PartitionSlave'
,'PartitionScheme'
,'PartitionType'
,'PartitionLabel'
,'PartitionUuid'
,'PartitionFlags'
,'PartitionNumber'
,'PartitionOffset'
,'PartitionSize'
,'PartitionAlignmentOffset'
,'PartitionTableScheme'
,'PartitionTableCount'
,'DriveVendor'
,'DriveModel'
,'DriveRevision'
,'DriveSerial'
#,'DriveWwn'
#,'DriveRotationRate'
#,'DriveWriteCache'
,'DriveConnectionInterface'
,'DriveConnectionSpeed'
#,'DriveMediaCompatibility'
#,'DriveMedia'
#,'DriveIsMediaEjectable'
#,'DriveCanDetach'
#,'DriveCanSpindown'
#,'DriveIsRotational'
#,'DriveAdapter'
#,'DrivePorts'
#,'DriveSimilarDevices'
]


class DeviceAddedListener:
    def __init__(self):

        self.bus = dbus.SystemBus()
        self.ud_manager_obj = self.bus.get_object("org.freedesktop.UDisks", 
                                                   "/org/freedesktop/UDisks")

        self.ud_manager = dbus.Interface(self.ud_manager_obj,
                                          "org.freedesktop.UDisks")

        self.ud_manager.connect_to_signal("DeviceAdded", self._filter)

    def _filter(self, dev):
        device_obj = self.bus.get_object("org.freedesktop.UDisks", dev)
        device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
        print '--------- event'
        for p in props:
            print p, "=", device_props.Get('org.freedesktop.UDisks.Device', p)
        print '---------'




if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    DeviceAddedListener()
    loop.run()

