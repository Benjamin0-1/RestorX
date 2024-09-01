from rest_framework.decorators import api_view
from rest_framework.response import Response
from restaurant.middlewares.is_waiter import waiter_only

@api_view(['GET'])
@waiter_only
def view_orders(request):
    return Response({'message': 'Orders view'})