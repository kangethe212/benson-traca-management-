from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

from .models import Property, PropertyMedia


@staff_member_required
def bulk_media_upload(request, property_id):
    """Custom admin view for bulk media upload"""
    try:
        property_obj = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        messages.error(request, 'Property not found.')
        return redirect('admin:listings_property_changelist')
    
    if request.method == 'POST':
        files = request.FILES.getlist('media_files')
        media_type = request.POST.get('media_type', 'image')
        
        uploaded_count = 0
        for file in files:
            # Generate unique filename
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save file
            file_path = default_storage.save(f'properties/{unique_filename}', ContentFile(file.read()))
            
            # Create PropertyMedia object
            PropertyMedia.objects.create(
                property=property_obj,
                media_type=media_type,
                file=file_path,
                caption=f"Uploaded: {file.name}",
                is_primary=False,
                order=PropertyMedia.objects.filter(property=property_obj).count() + 1
            )
            uploaded_count += 1
        
        messages.success(request, f'Successfully uploaded {uploaded_count} media files to {property_obj.title}.')
        return redirect('admin:listings_property_change', property_id)
    
    context = {
        'property': property_obj,
        'title': f'Bulk Media Upload - {property_obj.title}',
        'opts': Property._meta,
    }
    return render(request, 'admin/listings/property/bulk_media_upload.html', context)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def ajax_media_upload(request, property_id):
    """AJAX endpoint for media upload"""
    try:
        property_obj = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    media_type = request.POST.get('media_type', 'image')
    caption = request.POST.get('caption', f'Uploaded: {file.name}')
    
    # Generate unique filename
    file_extension = os.path.splitext(file.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Save file
    file_path = default_storage.save(f'properties/{unique_filename}', ContentFile(file.read()))
    
    # Create PropertyMedia object
    media_obj = PropertyMedia.objects.create(
        property=property_obj,
        media_type=media_type,
        file=file_path,
        caption=caption,
        is_primary=False,
        order=PropertyMedia.objects.filter(property=property_obj).count() + 1
    )
    
    return JsonResponse({
        'success': True,
        'media_id': media_obj.id,
        'file_url': media_obj.file.url,
        'caption': media_obj.caption
    })


@staff_member_required
def property_media_manager(request, property_id):
    """Enhanced media manager for properties"""
    try:
        property_obj = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        messages.error(request, 'Property not found.')
        return redirect('admin:listings_property_changelist')
    
    media_files = property_obj.media.all().order_by('order')
    
    context = {
        'property': property_obj,
        'media_files': media_files,
        'title': f'Media Manager - {property_obj.title}',
        'opts': Property._meta,
    }
    return render(request, 'admin/listings/property/media_manager.html', context)
