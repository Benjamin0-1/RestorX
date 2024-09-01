from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, ProductVariant, Image
from restaurant.user.models import AuditLog, User
from restaurant.utils.jwt_utils import create_access_token, create_refresh_token, get_user_from_jwt, verify_refresh_token, verify_access_token, decode_access_token, decode_refresh_token
from restaurant.middlewares.is_authenticated import jwt_required 
from restaurant.middlewares import is_authenticated, is_admin, is_waiter
from math import ceil

'''
    A waiter can see orders, a waiter can mark orders as complete.
    An admin can do everything including: CRUD products, CRUD product variants, CRUD users (also fire waiters by removing Role), CRUD orders, CRUD order items.
'''

@api_view(['POST'])
@jwt_required
@is_admin
def create_product(request):
    data = request.data
    name = data.get('name') # base plate name, not the variant name

    product_exists = Product.objects.filter(name=name).exists()
    if product_exists:
        return Response({'error': 'Product already exists'}, status=400)
    
    try:
        product = Product.objects.create(name=name)
        return Response({'success': 'Product created'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['PUT'])
@jwt_required
@is_admin
def update_product(request):
    data = request.data
    product_id = data.get('product_id')
    name = data.get('name')

    if not all([product_id, name]):
        return Response({'error': 'Missing required fields'}, status=400)
    
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({'error': 'Product not found'}, status=404)
    
    product_exists = Product.objects.filter(name=name).exists()
    if product_exists:
        return Response({'error': 'Product already exists'}, status=400)
    
    try:
        product.name = name
        product.save()
        return Response({'success': 'Product updated'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@jwt_required
@is_admin
def create_product_variant(request):
    data = request.data
    product_id = data.get('product_id')  # base plate id
    description = data.get('description')  # optional example: the best lasagna in town
    name = data.get('name')  # variant name, e.g., large pepperoni pizza
    price = data.get('price')
    images = data.get('images')  # list of image URLs, array

    if not all([name, price]):
        return Response({'error': 'Missing required fields'}, status=400)
    

    base_product = Product.objects.filter(id=product_id).first()
    if not base_product:
        return Response({'error': 'Base plate not found'}, status=404)
    

    variant_exists = ProductVariant.objects.filter(product=base_product, name=name).first()
    if variant_exists:
        return Response({'error': 'Variant already exists'}, status=400)
    
    try:
     
        product_variant = ProductVariant.objects.create(
            product=base_product,
            name=name,
            price=price,
            description=description if description else None
        )

        if images:
            for image_url in images:
                Image.objects.create(
                    product_variant=product_variant,
                    url=image_url
                )

        AuditLog.objects.create(
            user=request.user,
            action=f"Product variant created: {name}",
            action_ip=request.META.get('REMOTE_ADDR'),
        )

        return Response({'success': 'Product variant created'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

    

# route in which a user can all all the variants, images and their base plate as 'categories'
# this combines all filters as well, and pagination.
# if no filters are provided, return all in a list of pagination.
# this dynamically constrcuts the query based on the filters provided.
# example URL : http://127.0.0.1:8000/products?product_id=1&variant_id=1&min_price=10&max_price=20&variant_name=pepperoni&order=asc
@api_view(['GET'])
    # FOR NOW:
def get_products(request):
    data = request.query_params
    page = int(data.get('page', 1))  # Default to page 1 if not provided
    limit = int(data.get('limit', 5))  # Default to 5 items per page if not provided
    product_id = data.get('product_id')
    variant_id = data.get('variant_id')
    min_price = data.get('min_price')
    max_price = data.get('max_price')
    variant_name = data.get('variant_name')
    order = data.get('order', 'asc')  

    # Base query: Only active variants should be shown.
    query = ProductVariant.objects.filter(is_active=True)


    if product_id:
        query = query.filter(product_id=product_id)
    if variant_id:
        query = query.filter(id=variant_id)
    if min_price:
        query = query.filter(price__gte=min_price)
    if max_price:
        query = query.filter(price__lte=max_price)
    if variant_name:
        query = query.filter(name__icontains=variant_name)


    if order == 'asc':
        query = query.order_by('name')
    else:
        query = query.order_by('-name')


    total = query.count()
    total_pages = ceil(total / limit)
    offset = (page - 1) * limit
    query = query[offset:offset + limit]


    data = [{
        'id': variant.id,
        'product_id': variant.product.id,
        'product_name': variant.product.name,
        'name': variant.name,
        'price': variant.price,
        'stock': variant.stock,
        'description': variant.description,
        'is_active': variant.is_active,
        'images': [image.url for image in variant.images.all()]
    } for variant in query]

    # Response structure with pagination info
    return Response({
        'total': total,
        'total_pages': total_pages,
        'current_page': page,
        'data': data
    }, status=200)





@api_view(['DELETE']) 
@jwt_required
@is_admin
def delete_variant(request):
    data = request.data
    variant_id = data.get('variant_id')

    if not variant_id:
        return Response({'error': 'Missing required fields'}, status=400)
    
    variant = ProductVariant.objects.filter(id=variant_id).first()
    if not variant:
        return Response({'error': 'Variant not found'}, status=404)
    
    if variant.is_active == False:
        return Response({'error': 'Variant already disabled'}, status=400)
    
    try:
        variant.is_active = True # soft delete

        AuditLog.objects.create(
            user=request.user,
            action=f"Product variant disabled: {variant.name}",
            action_ip=request.META.get('REMOTE_ADDR'),
        )

        return Response({'success': 'Variant disabled'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['GET'])
def variant_detail(request, variant_id):
    variant = ProductVariant.objects.filter(id=variant_id).first()
    if not variant:
        return Response({'error': 'Variant not found'}, status=404)
    
    if variant.is_active == False:
        return Response({'error': 'Variant is disabled'}, status=400)
    
    images = []
    for image in variant.images.all():
        images.append(image.url)
    
    return Response({
        'id': variant.id,
        'product_id': variant.product.id,
        'product_name': variant.product.name,
        'name': variant.name,
        'price': variant.price,
        'stock': variant.stock,
        'description': variant.description,
        'is_active': variant.is_active,
        'images': images
    }, status=200)

