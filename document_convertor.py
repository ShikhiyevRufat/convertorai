def document_convertor():
    import subprocess
    import os
    from PIL import Image

    LIBREOFFICE_PATH = r'C:\Program Files\LibreOffice\program\soffice.exe'  

    def convert_to_pdf(input_file, output_file):
        extension = os.path.splitext(input_file)[1].lower()
        
        if extension in ['.docx', '.doc']:
            convert_word_to_pdf(input_file, output_file)
        elif extension in ['.xlsx', '.xls']:
            convert_excel_to_pdf(input_file, output_file)
        elif extension in ['.pptx', '.ppt']:
            convert_pptx_to_pdf(input_file, output_file)
        elif extension in ['.html']:
            convert_html_to_pdf(input_file, output_file)
        else:
            print(f"Unsupported file type: {extension}")

    def convert_word_to_pdf(input_file, output_file):
        command = [
            LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', 
            '--outdir', os.path.dirname(output_file), input_file
        ]
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to PDF and saved in {os.path.dirname(output_file)}.")

    def convert_excel_to_pdf(input_file, output_file):
        command = [
            LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', 
            '--outdir', os.path.dirname(output_file), input_file
        ]
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to PDF and saved in {os.path.dirname(output_file)}.")

    def convert_pptx_to_pdf(input_file, output_file):
        command = [
            LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', 
            '--outdir', os.path.dirname(output_file), input_file
        ]
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to PDF and saved in {os.path.dirname(output_file)}.")

    def convert_html_to_pdf(input_file, output_file):
        command = [
            LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', 
            '--outdir', os.path.dirname(output_file), input_file
        ]
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to PDF and saved in {os.path.dirname(output_file)}.")

    def convert_image_to_pdf(input_file, output_file):
        with Image.open(input_file) as img:
            img.convert('RGB').save(output_file, "PDF")
        print(f"Converted {input_file} to PDF and saved as {output_file}.")

    convert_to_pdf('my.pptx', 'output/output.pdf')
