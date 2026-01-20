import unittest
from unittest.mock import MagicMock, patch
from autoconfigoscli.core.remote.ssh import SSHWrapper
from autoconfigoscli.core.remote.manager import RemoteManager

class TestRemoteSSH(unittest.TestCase):
    def test_ssh_command_builder(self):
        ssh = SSHWrapper(port=2222, key_path="/tmp/key.pem")
        # Access private method for testing logic
        cmd = ssh._build_base_cmd("user@host")
        
        self.assertIn("-p", cmd)
        self.assertIn("2222", cmd)
        self.assertIn("-i", cmd)
        self.assertIn("/tmp/key.pem", cmd)
        self.assertIn("user@host", cmd)

    @patch("autoconfigoscli.core.remote.ssh.subprocess.run")
    def test_run_command_sudo(self, mock_run):
        ssh = SSHWrapper()
        
        # Mock success
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "OK"
        mock_res.stderr = ""
        mock_run.return_value = mock_res
        
        ok, out, err = ssh.run_command("host", "apt update", sudo=True)
        
        self.assertTrue(ok)
        # Check if sudo -n was prepended
        args, _ = mock_run.call_args
        full_cmd = args[0]
        self.assertTrue(any("sudo -n apt update" in str(c) for c in full_cmd) or "sudo -n apt update" in full_cmd[-1])

    @patch("autoconfigoscli.core.remote.bootstrap.BootstrapManager.check_dependencies")
    @patch("autoconfigoscli.core.remote.bootstrap.BootstrapManager.deploy_tool")
    @patch("autoconfigoscli.core.remote.ssh.SSHWrapper.run_command")
    def test_remote_install_flow(self, mock_ssh_run, mock_deploy, mock_check_deps):
        # Setup mocks
        mock_check_deps.return_value = (True, [])
        mock_deploy.return_value = (True, "/tmp/remote-repo")
        
        # Mock SSH execution of the install command
        mock_ssh_run.return_value = (True, "Install Done", "")
        
        rman = RemoteManager()
        res = rman.install_profile("tgt", "my-profile", dry_run=True)
        
        self.assertTrue(res["success"])
        self.assertEqual(res["stdout"], "Install Done")
        
        # Verify the install command structure
        # We expect: cd /tmp/remote-repo && source venv/bin/activate && python3 -m ...
        # Check call args of mock_ssh_run
        calls = mock_ssh_run.call_args_list
        # The second to last call should be the install command (last is cleanup)
        install_call_args = calls[-2][0] # (target, cmd)
        cmd_sent = install_call_args[1]
        
        self.assertIn("cd /tmp/remote-repo", cmd_sent)
        self.assertIn("install my-profile", cmd_sent)
        self.assertIn("--dry-run", cmd_sent)

if __name__ == '__main__':
    unittest.main()
