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

from .models import Property, PropertyMedia, Tenant, Lease


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


@staff_member_required
def tenant_approval_dashboard(request):
    """Dedicated tenant approval dashboard for admins"""
    from django.utils import timezone
    
    # Handle approval/rejection actions
    if request.method == 'POST':
        action = request.POST.get('action')
        tenant_id = request.POST.get('tenant_id')
        
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            
            if action == 'approve':
                tenant.is_verified = True
                tenant.save()
                messages.success(request, f'✅ {tenant.full_name} has been approved and verified!')
            elif action == 'reject':
                tenant.is_active = False
                tenant.save()
                messages.warning(request, f'❌ {tenant.full_name} has been rejected and deactivated.')
            
        except Tenant.DoesNotExist:
            messages.error(request, 'Tenant not found.')
        
        return redirect('listings:admin_tenant_approval')
    
    # Get all tenants with statistics
    all_tenants = Tenant.objects.select_related('user').order_by('-created_at')
    
    pending_tenants = all_tenants.filter(is_verified=False, is_active=True)
    verified_tenants = all_tenants.filter(is_verified=True, is_active=True)
    rejected_tenants = all_tenants.filter(is_active=False)
    
    # Get tenants with active leases
    tenants_with_leases = all_tenants.filter(
        leases__end_date__gte=timezone.now().date(),
        leases__status='active'
    ).distinct()
    
    context = {
        'pending_tenants': pending_tenants,
        'verified_tenants': verified_tenants,
        'rejected_tenants': rejected_tenants,
        'tenants_with_leases': tenants_with_leases,
        'stats': {
            'total': all_tenants.count(),
            'pending': pending_tenants.count(),
            'verified': verified_tenants.count(),
            'rejected': rejected_tenants.count(),
            'with_leases': tenants_with_leases.count(),
        },
        'title': 'Tenant Approval Dashboard',
    }
    
    return render(request, 'admin/tenant_approval.html', context)
