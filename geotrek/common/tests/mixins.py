import json
import os
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from rest_framework.reverse import reverse

from geotrek.common.parsers import DownloadImportError


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class GeotrekParserTestMixin:
    def mock_json(self):
        filename = os.path.join(
            "geotrek",
            self.mock_json_order[self.mock_time][0],
            "tests",
            "data",
            "geotrek_parser_v2",
            self.mock_json_order[self.mock_time][1],
        )
        self.mock_time += 1
        if (
            "trek_not_found" in filename
            or "trek_unpublished_practice_not_found" in filename
        ):
            msg = "404 Does not exist"
            raise DownloadImportError(msg)
        with open(filename) as f:
            return json.load(f)


class AttachmentTestMixin:
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def validate_attachment_creation(self, url, target, content_type):
        content = b"%PDF-1.4 fake pdf content, not a real image"
        file = SimpleUploadedFile("doc.pdf", content, content_type="application/pdf")

        data = {
            "content_type": content_type.pk,
            "object_id": target.pk,
            "attachment_file": file,
            "title": "title",
            "author": "author",
        }

        response = self.client.post(
            reverse(url, args=[target.id]),
            data=data,
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        attachments = target.attachments.all()
        self.assertEqual(attachments.count(), 1)
        attachment = attachments[0]
        self.assertTrue(
            attachment.attachment_file.storage.exists(attachment.attachment_file.name)
        )
        self.assertEqual(attachment.attachment_file.size, len(content))
        self.assertEqual(attachment.filetype.type, "Photographie")
