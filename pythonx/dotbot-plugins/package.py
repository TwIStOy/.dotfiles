from subprocess import CalledProcessError, check_call, DEVNULL
from typing import Any, Dict, List, Sequence, Union
import os
import sys
import subprocess

import dotbot



class Apt(dotbot.Plugin):
    def can_handle(self, directive: str) -> bool:
        return directive == 'package' and sys.platform != 'darwin'

    def handle(self, directive: str, packages: List[Union[str, Dict]]) -> bool:
        p = sys.platform
        installed_packages = []
        for pkg in packages:
            if type(pkg) == str:
                installed_packages.append(pkg)
            elif type(pkg) == dict:
                p_pkg = pkg.get(p, None)
                if p_pkg is not None:
                    installed_packages.append(p_pkg)
        self._log.info( 'Installing packages using APT: {}'.format(', '.join(installed_packages)))

        res = True
        res = res and self._run([
            'sudo', 'sed', '-i', 's/security.ubuntu.com/mirrors.ustc.edu.cn/g', '/etc/apt/sources.list'
            ], 'Install USTC mirror step 1')
        res = res and self._run([
            'sudo', 'sed', '-i', 's/cn.archive.ubuntu.com/mirrors.ustc.edu.cn/g', '/etc/apt/sources.list'
            ], 'Install USTC mirror step 2')
        res = res and self._run([
            'sudo', 'sed', '-i', 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g', '/etc/apt/sources.list'
            ], 'Install USTC mirror step 3')
        res = res and self._run(['sudo', 'apt', 'update'], "Updating APT")
        res = res and self._run(['sudo', 'apt', 'install', '-y'] + installed_packages, "All packages are installed")
        return res

    def _run(self, command: Sequence[Any], low_info: str) -> bool:
        self._log.lowinfo(low_info)
        try:
            check_call(command, stdout=DEVNULL, stderr=DEVNULL)
            return True
        except CalledProcessError as e:
            self._log.error(e)
            return False


class Brew(dotbot.Plugin):
    def can_handle(self, directive: str) -> bool:
        return directive == 'package' and sys.platform == 'darwin'

    def handle(self, directive: str, packages: List[Union[str, Dict]]) -> bool:
        p = sys.platform
        self._bootstrap_brew()
        self._bootstrap_cask()

        installed_packages = []
        for pkg in packages:
            if type(pkg) == str:
                installed_packages.append(pkg)
            elif type(pkg) == dict:
                p_pkg = pkg.get(p, None)
                if p_pkg is not None:
                    installed_packages.append(p_pkg)

        self._log.info('Installing package using brew/brew cask: {}'.format(', '.join(installed_packages)))

        return self._process_data('brew install', installed_packages)

    def _bootstrap(self, cmd):
        with open(os.devnull, 'w') as devnull:
            stdin = stdout = stderr = devnull
            subprocess.call(cmd, shell=True, stdin=stdin, stdout=stdout, stderr=stderr,
                            cwd=self._context.base_directory())
    def _tap(self, tap_list):
        cwd = self._context.base_directory()
        log = self._log
        with open(os.devnull, 'w') as devnull:
            stdin = stdout = stderr = devnull
            for tap in tap_list:
                log.info("Tapping %s" % tap)
                cmd = "brew tap %s" % (tap)
                result = subprocess.call(cmd, shell=True, cwd=cwd)

                if result != 0:
                    log.warning('Failed to tap [%s]' % tap)
                    return False
            return True

    def _bootstrap_brew(self):
        import platform
        link = "https://raw.githubusercontent.com/Homebrew/install/master/install"
        if platform.system() == 'Linux':
            link = "https://raw.githubusercontent.com/Linuxbrew/install/master/install"

        cmd = """hash brew || ruby -e "$(curl -fsSL {0})";
              brew update""".format(link)
        self._bootstrap(cmd)

    def _bootstrap_cask(self):
        self._bootstrap_brew()
        cmd = "brew tap caskroom/cask"
        self._bootstrap(cmd)

    def _process_data(self, install_cmd, data):
        success = self._install(install_cmd, data)
        if success:
            self._log.info('All packages have been installed')
        else:
            self._log.error('Some packages were not installed')
        return success

    def _install(self, install_cmd, packages_list):
        cwd = self._context.base_directory()
        log = self._log
        with open(os.devnull, 'w') as devnull:
            stdin = stdout = stderr = devnull
            for package in packages_list:
                if install_cmd == 'brew install':
                    cmd = "brew ls --versions %s" % package
                else:
                    cmd = "brew cask ls --versions %s" % package
                isInstalled = subprocess.call(cmd, shell=True, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd)
                if isInstalled != 0:
                    log.info("Installing %s" % package)
                    cmd = "%s %s" % (install_cmd, package)
                    result = subprocess.call(cmd, shell=True, cwd=cwd)
                    if result != 0:
                        log.warning('Failed to install [%s]' % package)
                        return False
            return True
