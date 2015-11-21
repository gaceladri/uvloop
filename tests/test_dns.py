import asyncio
import socket
import uvloop
import unittest

from uvloop import _testbase as tb


_HOST, _PORT = ('example.com', 80)
_NON_HOST, _NON_PORT = ('a' + '1' * 50 + '.wat', 800)


class BaseTestDNS:

    def _test_getaddrinfo(self, *args, **kwargs):
        err = None
        try:
            a1 = socket.getaddrinfo(*args, **kwargs)
        except socket.gaierror as ex:
            err = ex

        try:
            a2 = self.loop.run_until_complete(
                self.loop.getaddrinfo(*args, **kwargs))
        except socket.gaierror as ex:
            if err is not None:
                self.assertEqual(ex.args, err.args)
            else:
                raise
        else:
            if err is not None:
                self.fail(
                    'uv failed, but blocking getaddrinfo run without error')

            self.assertEqual(a1, a2)

    def test_getaddrinfo_1(self):
        self._test_getaddrinfo(_HOST, _PORT)

    def test_getaddrinfo_2(self):
        self._test_getaddrinfo(_HOST, _PORT, flags=socket.AI_CANONNAME)

    def test_getaddrinfo_3(self):
        self._test_getaddrinfo(_NON_HOST, _NON_PORT)

    def test_getaddrinfo_4(self):
        self._test_getaddrinfo(_HOST, _PORT, family=-1)


class Test_UV_DNS(BaseTestDNS, tb.UVTestCase):

    def test_getaddrinfo_close_loop(self):
        try:
            # Check that we have internet connection
            socket.getaddrinfo(_HOST, _PORT)
        except socket.error:
            raise unittest.SkipTest

        async def run():
            fut = self.loop.getaddrinfo(_HOST, _PORT)
            fut.cancel()
            self.loop.stop()

        try:
            self.loop.run_until_complete(run())
        finally:
            self.loop.close()


class Test_AIO_DNS(BaseTestDNS, tb.AIOTestCase):
    pass
