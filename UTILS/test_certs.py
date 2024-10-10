# Cert verification
# Does not work if problem is in my/your system: i.e. the Python incompatability if version higher than 3.9
# Not my code, hacked together from web


import ssl
import requests
import platform
from datetime import datetime
from cryptography import x509


def get_cert_for_hostname(hostname, port):
    conn = ssl.create_connection((hostname, port))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sock = context.wrap_socket(conn, server_hostname=hostname)
    certDER = sock.getpeercert(True)
    certPEM = ssl.DER_cert_to_PEM_cert(certDER)
    conn.close()
    return x509.load_pem_x509_certificate(certPEM.encode('ascii'))


def is_cert_expired(hostname, port):
    cert = get_cert_for_hostname(hostname, port)
    return datetime.now() > cert.not_valid_after


if __name__ == '__main__':
    print(f"Python version: {platform.python_version()}")
    print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
    print(f"requests version: {requests.__version__}")  #
    hosts = ['pris.iaea.org/PRIS/CountryStatistics/CountryStatisticsLandingPage.aspx']
    for host in hosts:
        try:
            requests.get(f"https://{host}")
            print(f"request for host {host} was successful")
        except BaseException as err:
            if is_cert_expired(host, 443):
                print(f"certificate for {host} expired")
            else:
                print(f"error {err} with {host}")