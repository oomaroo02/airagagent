import oci
from pdf2image import convert_from_path
from PIL import Image, ImageDraw 

# ---------------------------------------------------------------------------
def remove_entities(anonym_pdf_file, j):
    images = convert_from_path(anonym_pdf_file)
    page_count = len(images)
  
    if page_count == 1:
        boxes = [
            (0, 0, 10, 10),
            (width/2, height/2, 10, 10)
        ]
        draw_boxes(images[0], boxes)
    else:
        for image in images:
            boxes = [
                (0, 0, 10, 10),
                (width/2, height/2, 10, 10)
            ]
            draw_boxes(images[0], boxes)
    pdf_file= anonym_pdf_file.replace(".anonym.pdf", ".pdf")      
    saveAsPDF(pdf_file, images )  
    return pdf_file

# ---------------------------------------------------------------------------
def draw_boxes( image: Image.Image, boxes ):
    for i, (x, y, h, w) in enumerate(boxes):
        print(f"  x: {x}")
        print(f"  y: {y}")
        print(f"  h: {h}")
        print(f"  w: {w}")
        img1 = ImageDraw.Draw(image) 
        img1.rectangle( [(x, y), (x + w, y + h)], "#000" )

# ---------------------------------------------------------------------------
def saveAsPDF( file_name, images ):
    # Save image with PIL
    if len(images) == 1:
        images[0].save(file_name)
    else:
        im = images.pop(0)
        im.save(file_name, save_all=True,append_images=images)

# ---------------------------------------------------------------------------
def entities( j ):
    log( "<entities>")
    compartmentId = os.getenv("TF_VAR_compartment_ocid")
    
    documents = []
    # Parse the output of document understanding
    for p in j.get("pages"):
        pageNumber = p.get("pageNumber")
        page = ""
        for l in p.get("lines"):
            page += l.get("text") + "\n"
        doc_page = {
            "languageCode": "auto",
            "key": str(pageNumber),
            "text": page            
        }
        documents.append( doc_page )

    ai_client = oci.ai_language.AIServiceLanguageClient(config = {}, signer=signer)  
    details = {
        "documents": documents,
        "compartmentId": compartmentId
    }
    response = ai_client.batch_detect_language_entities( details )
    log( response.data )
    log( "</entities> ")
    return response.data


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    file_name = "anonymize/resume.pdf"
    images = convert_from_path(file_name)
    print( "Number of pages" + str(len(images)) )
  
    for image in images:
        width, height = image.size
        print( type(Image) )
        print( "Width="+ str(width) + " / Height="+ str(height) )
        boxes = [
            (0, 0, 10, 10),
            (width/2, height/2, 10, 10)
        ]
        draw_boxes( image, boxes)
    saveAsPDF( "anonymize/temp.pdf", images)
