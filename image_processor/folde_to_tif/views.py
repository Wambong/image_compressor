import os
import uuid
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import FolderUploadForm
from PIL import Image
import zipfile
import tempfile
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

from os import listdir
def upload_folder(request):
    if request.method == 'POST':
        form = FolderUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('files')
            image_list = []

            for file in uploaded_files:
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_path = fs.path(filename)
                image = Image.open(file_path)
                image_list.append(image)

            if image_list:
                base_path = os.path.join(settings.MEDIA_ROOT, 'result')
                for i, image in enumerate(image_list):
                    tiff_filename = f"{base_path}_{i + 1}.tif"  # Add numbering to filenames
                    image.save(tiff_filename, save_all=True, compression='tiff_deflate')

                zip_filename = os.path.join(settings.MEDIA_ROOT, 'converted_images.zip')
                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, image in enumerate(image_list):
                        tiff_filename = f"result_{i + 1}.tif"  # Adjust filename format if needed
                        file_path = os.path.join(settings.MEDIA_ROOT, tiff_filename)
                        zip_file.write(file_path, arcname=tiff_filename)

            for file in uploaded_files:
                fs.delete(file.name)
            context = {
                'form': form,
                'zip_file_url': os.path.join(settings.MEDIA_URL, 'converted_images.zip'),
            }

            return render(request, 'folde_to_tif/upload.html', context)
    else:
        form = FolderUploadForm()

    return render(request, 'folde_to_tif/upload.html', {'form': form})


@csrf_exempt
def select_directory(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')

        if files:
            # Convert files to TIFF and create a zip file
            temp_dir = tempfile.mkdtemp()
            zip_filename = os.path.join(temp_dir, 'converted_files.zip')
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in files:
                    # Load the image file
                    with Image.open(file) as image:
                        # Generate a unique file name
                        unique_name = f"{os.path.splitext(file.name)[0]}_{uuid.uuid4().hex}.tiff"
                        tiff_file_path = os.path.join(temp_dir, unique_name)
                        # Convert to TIFF format
                        image.save(tiff_file_path, 'TIFF')
                        # Add to zip file
                        zipf.write(tiff_file_path, os.path.basename(tiff_file_path))

            # Serve the zip file as a download
            response = FileResponse(open(zip_filename, 'rb'))
            response['Content-Disposition'] = 'attachment; filename="converted_files.zip"'
            return response
        else:
            return HttpResponse('Invalid directory selected')

    return render(request, 'folde_to_tif/success.html')