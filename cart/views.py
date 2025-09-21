from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from .models import Novel, Cart, CartItem
from .serializers import NovelSerializer, CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action

class NovelViewSet(viewsets.ReadOnlyModelViewSet):
    """小说视图集，用于获取小说列表和详情"""
    queryset = Novel.objects.all().order_by('rank')
    serializer_class = NovelSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """根据年份参数过滤小说列表"""
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        if year:
            # 根据年份字段过滤小说
            queryset = queryset.filter(year=year)
        return queryset

class AuthViewSet(viewsets.ViewSet):
    """用户认证视图集，处理登录、登出和注册操作"""
    permission_classes = [AllowAny]
    # 禁用CSRF保护
    authentication_classes = []
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """用户注册API"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            
            # 验证必要字段
            if not username or not email or not password or not confirm_password:
                return Response({'error': '所有字段都是必填的'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证密码是否匹配
            if password != confirm_password:
                return Response({'error': '两次输入的密码不匹配'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证密码长度
            if len(password) < 6:
                return Response({'error': '密码长度至少为6位'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查邮箱是否已被使用
            if User.objects.filter(email=email).exists():
                return Response({'error': '邮箱已被使用'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建新用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # 登录新用户
            login(request, user)
            
            return Response(
                {'success': True, 'message': '注册成功', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录API"""
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response(
                    {'error': '用户名和密码不能为空'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 验证用户凭据
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # 登录用户
                login(request, user)
                
                # 返回用户信息
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
                
                return Response(
                    {
                        'success': True,
                        'user': user_data,
                        'message': '登录成功'
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': '用户名或密码错误'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出API"""
        try:
            # 如果用户已登录，获取并清空购物车
            if request.user.is_authenticated:
                try:
                    # 获取用户的购物车
                    cart = Cart.objects.get(user=request.user)
                    # 清空购物车
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    # 如果购物车不存在，忽略
                    pass
            
            # 登出用户
            logout(request)
            
            return Response(
                {'success': True, 'message': '登出成功'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'])
    def logout_get(self, request):
        """使用GET方法的登出API，方便测试"""
        try:
            # 如果用户已登录，获取并清空购物车
            if request.user.is_authenticated:
                try:
                    # 获取用户的购物车
                    cart = Cart.objects.get(user=request.user)
                    # 清空购物车
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    # 如果购物车不存在，忽略
                    pass
            
            # 登出用户
            logout(request)
            
            return Response(
                {'success': True, 'message': '登出成功'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def current_user(self, request):
        """获取当前登录用户信息API"""
        if request.user.is_authenticated:
            user = request.user
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

class CartViewSet(viewsets.ViewSet):
    """购物车视图集，用于处理购物车的各种操作"""
    permission_classes = [AllowAny]
    # 临时禁用CSRF保护以解决添加购物车问题
    authentication_classes = []
    
    # 设置购物车保留策略：False表示用户会话结束后不保留购物车内容
    PERSIST_CART_AFTER_SESSION = False
    
    def get_cart(self, request):
        """获取当前用户的购物车，如果不存在则创建"""
        # 检查用户是否已登录
        if request.user.is_authenticated:
            # 如果用户已登录，获取或创建与用户关联的购物车
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # 如果用户未登录，使用session_key获取或创建购物车
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
                
            # 检查购物车是否存在
            try:
                cart = Cart.objects.get(session_key=session_key)
                
                # 如果不希望在会话结束后保留购物车内容，检查上次活动时间
                if not self.PERSIST_CART_AFTER_SESSION:
                    # 获取当前时间
                    current_time = timezone.now()
                    # 检查会话是否包含上次活动时间
                    last_activity = request.session.get('last_cart_activity')
                    
                    if last_activity:
                        # 转换为datetime对象
                        last_activity_time = timezone.datetime.fromisoformat(last_activity)
                        # 检查是否超过30分钟（1800秒）没有活动
                        time_diff = (current_time - last_activity_time).total_seconds()
                        if time_diff > 1800:  # 30分钟
                            # 清空购物车
                            cart.items.all().delete()
                
                # 更新会话中的最后活动时间
                request.session['last_cart_activity'] = timezone.now().isoformat()
            except Cart.DoesNotExist:
                # 如果购物车不存在，创建新的
                cart = Cart.objects.create(session_key=session_key)
                # 设置初始活动时间
                request.session['last_cart_activity'] = timezone.now().isoformat()
        return cart
    
    def list(self, request):
        """查看购物车内容"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    from django.views.decorators.csrf import csrf_exempt
    from django.utils.decorators import method_decorator
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """添加商品到购物车"""
        try:
            novel_id = request.data.get('novel_id')
            quantity = request.data.get('quantity', 1)
            
            if not novel_id:
                return Response({'error': '小说ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return Response({'error': '数量必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': '数量必须是整数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取购物车
            cart = self.get_cart(request)
            
            # 获取小说对象
            try:
                novel = Novel.objects.get(id=novel_id)
            except Novel.DoesNotExist:
                return Response({'error': '小说不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 检查购物车中是否已存在该商品
            cart_item, created = CartItem.objects.get_or_create(cart=cart, novel=novel)
            
            # 如果商品已存在，则增加数量
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                # 如果是新商品，则设置数量
                cart_item.quantity = quantity
                cart_item.save()
            
            # 返回更新后的购物车
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """更新购物车中商品的数量"""
        try:
            item_id = request.data.get('item_id')
            quantity = request.data.get('quantity')
            
            if not item_id or not quantity:
                return Response({'error': '商品ID和数量不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                quantity = int(quantity)
                # 允许负数用于减少数量
                if quantity == 0:
                    return Response({'error': '数量不能为0'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': '数量必须是整数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取购物车
            cart = self.get_cart(request)
            
            # 获取购物车项目
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
            except CartItem.DoesNotExist:
                return Response({'error': '购物车项目不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 更新数量
            # 如果是正数，则增加数量；如果是负数，则减少数量
            new_quantity = cart_item.quantity + quantity
            
            # 确保数量不小于1
            if new_quantity <= 0:
                # 如果数量小于等于0，则删除该商品
                cart_item.delete()
            else:
                # 否则更新数量
                cart_item.quantity = new_quantity
                cart_item.save()
            
            # 返回更新后的购物车
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """从购物车中删除商品"""
        try:
            item_id = request.query_params.get('item_id')
            
            if not item_id:
                return Response({'error': '商品ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取购物车
            cart = self.get_cart(request)
            
            # 获取购物车项目并删除
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                cart_item.delete()
            except CartItem.DoesNotExist:
                return Response({'error': '购物车项目不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 返回更新后的购物车
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """清空购物车"""
        try:
            # 获取购物车
            cart = self.get_cart(request)
            
            # 删除购物车中的所有商品
            cart.items.all().delete()
            
            # 返回更新后的购物车
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
