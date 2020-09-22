import pytest
from lib.common import cold_migration_then_come_back, live_storage_migration_then_come_back

# Requirements:
# From --hosts parameter:
# - host(A1): first XCP-ng host >= 8.2 with an additional unused disk for the SR.
# - hostA2: Second member of the pool. Can have any local SR.
# - hostB1: Master of a second pool. Any local SR.
# From --vm parameter
# - A VM to import to the ZFS SR
# And:
# - access to XCP-ng RPM repository from hostA1

@pytest.fixture(scope='module')
def zfs_sr(host, sr_disk):
    """ a ZFS SR on first host """
    assert not host.file_exists('/usr/sbin/zpool'), \
        "zfs must not be installed on the host at the beginning of the tests"
    host.yum_install(['zfs'])
    host.ssh(['modprobe', 'zfs'])
    host.ssh(['zpool', 'create', 'vol0', '/dev/' + sr_disk])
    sr = host.sr_create('zfs', "ZFS-local-SR", {'location': 'vol0'})
    yield sr
    # teardown
    sr.destroy()
    host.ssh(['zpool', 'destroy', 'vol0'])
    host.yum_remove(['zfs'])

@pytest.fixture(scope='module')
def vm_on_zfs_sr(host, zfs_sr, vm_ref):
    print(">> ", end='')
    vm = host.import_vm_url(vm_ref, sr_uuid=zfs_sr.uuid)
    yield vm
    # teardown
    print("<< Destroy VM")
    vm.destroy(verify=True)

class TestZFSSRMultiHost:
    def test_cold_intrapool_migration(self, host, hostA2, vm_on_zfs_sr, zfs_sr, local_sr_on_hostA2):
        cold_migration_then_come_back(vm_on_zfs_sr, host, zfs_sr, hostA2, local_sr_on_hostA2)

    def test_live_intrapool_migration(self, host, hostA2, vm_on_zfs_sr, zfs_sr, local_sr_on_hostA2):
        live_storage_migration_then_come_back(vm_on_zfs_sr, host, zfs_sr, hostA2, local_sr_on_hostA2)

    def test_cold_crosspool_migration(self, host, hostB1, vm_on_zfs_sr, zfs_sr, local_sr_on_hostB1):
        cold_migration_then_come_back(vm_on_zfs_sr, host, zfs_sr, hostB1, local_sr_on_hostB1)

    def test_live_crosspool_migration(self, host, hostB1, vm_on_zfs_sr, zfs_sr, local_sr_on_hostB1):
        live_storage_migration_then_come_back(vm_on_zfs_sr, host, zfs_sr, hostB1, local_sr_on_hostB1)
