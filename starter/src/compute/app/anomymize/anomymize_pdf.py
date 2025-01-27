import os
import tempfile
from pdf2image import convert_from_path
import cv2
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
def download_file(value):
    # Read the SITEMAP file from the object storage
    # The format of the file expected is a txt file. Each line contains a full URI.
    # Transforms all the links in PDF and reupload them as PDF in the same object storage
    log( "<download_file>")
    eventType = value["eventType"]     
    namespace = value["data"]["additionalDetails"]["namespace"]
    bucketName = value["data"]["additionalDetails"]["bucketName"]
    resourceName = value["data"]["resourceName"]
    os_client = oci.object_storage.ObjectStorageClient(config = {}, signer=signer)
    resp = os_client.get_object(namespace_name=namespace, bucket_name=bucketName, object_name=resourceName)
    file_name = LOG_DIR+"/"+UNIQUE_ID+".pdf"
    with open(file_name, 'wb') as f:
        for chunk in resp.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)
    return file_name

# ---------------------------------------------------------------------------
def anomymize_pdf(value, docu_json):
    file_name = download_file( value )
    images = convert_from_path(file_name)
    page_count = len(images)
  
    page_number = 1
    if page_count == 1:
        # return str if 1 page PDF, else a list of str
        find_emails(text=self.texts[0], matches=self.PII_objects)
        find_numbers(text=self.texts[0], matches=self.PII_objects)
        find_months(text=self.texts[0], matches=self.PII_objects)

        find_EOI(pipeline=ner, matches=self.PII_objects, EOI="PER")
        find_EOI(pipeline=ner, matches=self.PII_objects, EOI="ORG")
        find_EOI(pipeline=ner, matches=self.PII_objects, EOI="LOC")
        find_coordinates_pytesseract(matches=self.PII_objects,
                                        data=self.pages_data[page_number - 1],
                                        bbox=self.bbox)

        draw_boxes(image=self.images[0], box_list)
    else:
        self.images2text(self.images)

        for excerpt in self.texts:
            temp_pii = []
            temp_bbox = []
            ner = self._nlp(excerpt)

            find_emails(text=excerpt, matches=temp_pii)
            find_numbers(text=excerpt, matches=temp_pii)
            find_months(text=excerpt, matches=temp_pii)

            find_EOI(pipeline=ner, matches=temp_pii, EOI="PER")
            find_EOI(pipeline=ner, matches=temp_pii, EOI="ORG")
            find_EOI(pipeline=ner, matches=temp_pii, EOI="LOC")

            find_coordinates_pytesseract(  # noqa: F405
                matches=temp_pii,
                data=self.pages_data[page_number - 1],
                bbox=temp_bbox)
            self.cover_box(self.images[page_number - 1],
                            temp_bbox, fill=fill,
                            outline=outline)

            self.PII_objects.append({f'page_{page_number}': temp_pii})
            self.bbox.append({f'page_{page_number}': temp_bbox})

            page_number += 1

# ---------------------------------------------------------------------------
def draw_boxes( image: Image.Image, boxes ):
    color = (0, 255, 0)
    for i, (x, y, h, w) in enumerate(boxes):
        print(f"  x: {x}")
        print(f"  y: {y}")
        print(f"  h: {h}")
        print(f"  w: {w}")
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

# ---------------------------------------------------------------------------
def saveAsPDF( file_name, images ):
    # Save image with PIL
    if len(images) == 1:
        images[0].save(file_name)
    else:
        im = images.pop(0)
        im.save(file_name, save_all=True,append_images=images)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    file_name = " resume.pdf"
    images = convert_from_path(file_name)
    nb_pages = len(images)
    print( nb_pages )
  
    for image in images:
        width, height = image.size
        print( "Width="+width + " / Height="+height )
        boxes = [
            (0, 0, 10, 10),
            (width/2, height/2, 10, 10)
        ]
        draw_boxes( image, boxes)
    saveAsPDF( "temp.pdf", images)
