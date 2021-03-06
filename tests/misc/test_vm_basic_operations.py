import pytest
from lib.common import wait_for_not

pytestmark = pytest.mark.default_vm('mini-linux-x86_64-bios')

def test_pause(running_vm):
    vm = running_vm
    vm.pause(verify=True)
    vm.unpause()
    vm.wait_for_vm_running_and_ssh_up()

def test_suspend(running_vm):
    vm = running_vm
    vm.suspend(verify=True)
    vm.resume()
    vm.wait_for_vm_running_and_ssh_up()

def test_snapshot(running_vm):
    vm = running_vm
    vm.test_snapshot_on_running_vm()

def test_checkpoint(running_vm):
    vm = running_vm
    print("Start a 'sleep' process on VM through SSH")
    pid = vm.start_background_process('sleep 10000')
    snapshot = vm.checkpoint()
    filepath = '/tmp/%s' % snapshot.uuid
    vm.ssh_touch_file(filepath)
    snapshot.revert()
    vm.resume()
    vm.wait_for_vm_running_and_ssh_up()
    print("Check file does not exist anymore")
    vm.ssh(['test ! -f ' + filepath])
    print("Check 'sleep' process is still running")
    assert vm.pid_exists(pid)
    print("Kill background process")
    vm.ssh(['kill ' + pid])
    wait_for_not(lambda: vm.pid_exists(pid), "Wait for process %s not running anymore" % pid)
    snapshot.destroy(verify=True)
