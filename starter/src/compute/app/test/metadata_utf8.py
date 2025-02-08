import os
import oci
from oci.object_storage.transfer.constants import MEBIBYTE

namespace = os.getenv("NAMESPACE")
bucketName = os.getenv("BUCKET_NAME")
resourceName = "file.txt"
    
metadata = { "key": "日本語" }
fileName = "/tmp/"+resourceName
with open(fileName, 'w') as f:
    f.write("Hello World")

signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
os_client = oci.object_storage.ObjectStorageClient(config = {}, signer=signer)

signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
upload_manager = oci.object_storage.UploadManager(os_client, max_parallel_uploads=10)
upload_manager.upload_file(
  namespace_name=namespace, 
  bucket_name=bucketName, 
  object_name=resourceName, 
  file_path=fileName, 
  part_size=2 * MEBIBYTE, 
  content_type="text/html", 
  metadata=metadata
)

"""
 error
 Traceback (most recent call last):
  File "/home/opc/app/test.py", line 19, in <module>
    upload_manager.upload_file(
  File "/home/opc/.local/lib/python3.9/site-packages/oci/object_storage/transfer/upload_manager.py", line 254, in upload_file
    return self._upload_singlepart(namespace_name, bucket_name, object_name, file_path, **kwargs)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/object_storage/transfer/upload_manager.py", line 374, in _upload_singlepart
    response = self.object_storage_client.put_object(namespace_name,
  File "/home/opc/.local/lib/python3.9/site-packages/oci/object_storage/object_storage_client.py", line 5749, in put_object
    return retry_strategy.make_retrying_call(
  File "/home/opc/.local/lib/python3.9/site-packages/oci/retry/retry.py", line 308, in make_retrying_call
    response = func_ref(*func_args, **func_kwargs)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/base_client.py", line 519, in call_api
    return self.request(request, allow_control_chars, operation_name, api_reference_link)
  File "/home/opc/.local/lib/python3.9/site-packages/circuitbreaker.py", line 146, in wrapper
    return self.call(function, *args, **kwargs)
  File "/home/opc/.local/lib/python3.9/site-packages/circuitbreaker.py", line 188, in call
    return func(*args, **kwargs)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/base_client.py", line 670, in request
    response = self.session.request(
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/requests/sessions.py", line 536, in request
    resp = self.send(prep, **send_kwargs)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/requests/sessions.py", line 652, in send
    r = adapter.send(request, **kwargs)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/requests/adapters.py", line 447, in send
    resp = conn.urlopen(
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/urllib3/connectionpool.py", line 721, in urlopen
    httplib_response = self._make_request(
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/urllib3/connectionpool.py", line 421, in _make_request
    conn.request(method, url, **httplib_request_kw)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/urllib3/connection.py", line 249, in request
    super(HTTPConnection, self).request(method, url, body=body, headers=headers)
  File "/usr/lib64/python3.9/http/client.py", line 1285, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/base_client.py", line 181, in _send_request
    rval = super(OCIConnection, self)._send_request(
  File "/usr/lib64/python3.9/http/client.py", line 1326, in _send_request
    self.putheader(hdr, value)
  File "/home/opc/.local/lib/python3.9/site-packages/oci/_vendor/urllib3/connection.py", line 229, in putheader
    _HTTPConnection.putheader(self, header, *values)
  File "/usr/lib64/python3.9/http/client.py", line 1258, in putheader
    values[i] = one_value.encode('latin-1')
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 0-2: ordinal not in range(256)
"""