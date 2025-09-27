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
    """小説ビューセット、小説リストと詳細を取得するために使用"""
    queryset = Novel.objects.all().order_by('rank')
    serializer_class = NovelSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """年パラメータによって小説リストをフィルタリング"""
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        if year:
            # 年フィールドによって小説をフィルタリング
            queryset = queryset.filter(year=year)
        return queryset

class AuthViewSet(viewsets.ViewSet):
    """ユーザー認証ビューセット、ログイン、ログアウト、登録操作を処理"""
    permission_classes = [AllowAny]
    # CSRF保護を無効にする
    authentication_classes = []
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """ユーザー登録API"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            
            # 必須フィールドを検証
            if not username or not email or not password or not confirm_password:
                return Response({'error': 'すべてのフィールドは必須です'}, status=status.HTTP_400_BAD_REQUEST)
            
            # パスワードが一致するか検証
            if password != confirm_password:
                return Response({'error': '入力したパスワードが一致しません'}, status=status.HTTP_400_BAD_REQUEST)
            
            # パスワードの長さを検証
            if len(password) < 6:
                return Response({'error': 'パスワードの長さは少なくとも6文字必要です'}, status=status.HTTP_400_BAD_REQUEST)
            
            # ユーザー名が既に存在するか確認
            if User.objects.filter(username=username).exists():
                return Response({'error': 'ユーザー名は既に存在します'}, status=status.HTTP_400_BAD_REQUEST)
            
            # メールアドレスが既に使用されているか確認
            if User.objects.filter(email=email).exists():
                return Response({'error': 'メールアドレスは既に使用されています'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 新しいユーザーを作成
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # 新しいユーザーをログインさせる
            login(request, user)
            
            return Response(
                {'success': True, 'message': '登録が成功しました', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['post'])
    def login(self, request):
        """ユーザーログインAPI"""
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response(
                    {'error': 'ユーザー名とパスワードは必須です'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ユーザーの認証情報を検証
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # ユーザーをログインさせる
                login(request, user)
                
                # ユーザー情報を返す
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
                        'message': 'ログインが成功しました'
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'ユーザー名またはパスワードが間違っています'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """ユーザーログアウトAPI"""
        try:
            # ユーザーがログインしている場合、カートを取得して空にする
            if request.user.is_authenticated:
                try:
                    # ユーザーのカートを取得
                    cart = Cart.objects.get(user=request.user)
                    # カートを空にする
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    # カートが存在しない場合は無視
                    pass
            
            # ユーザーをログアウトさせる
            logout(request)
            
            return Response(
                {'success': True, 'message': 'ログアウトが成功しました'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'])
    def logout_get(self, request):
        """テスト用のGETメソッドを使用したログアウトAPI"""
        try:
            # ユーザーがログインしている場合、カートを取得して空にする
            if request.user.is_authenticated:
                try:
                    # ユーザーのカートを取得
                    cart = Cart.objects.get(user=request.user)
                    # カートを空にする
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    # カートが存在しない場合は無視
                    pass
            
            # ユーザーをログアウトさせる
            logout(request)
            
            return Response(
                {'success': True, 'message': 'ログアウトが成功しました'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def current_user(self, request):
        """現在ログイン中のユーザー情報を取得するAPI"""
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
            return Response({'error': 'ログインしていません'}, status=status.HTTP_401_UNAUTHORIZED)

class CartViewSet(viewsets.ViewSet):
    """カートビューセット、カートの様々な操作を処理するために使用"""
    permission_classes = [AllowAny]
    # カート追加の問題を解決するために一時的にCSRF保護を無効にする
    authentication_classes = []
    
    # カートの保持戦略を設定：Falseはセッション終了後にカートの内容を保持しないことを意味する
    PERSIST_CART_AFTER_SESSION = False
    
    def get_cart(self, request):
        """現在のユーザーのカートを取得し、存在しない場合は作成する"""
        # ユーザーがログインしているか確認
        if request.user.is_authenticated:
            # ユーザーがログインしている場合、ユーザーに関連するカートを取得または作成
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # ユーザーがログインしていない場合、session_keyを使用してカートを取得または作成
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
                
            # カートが存在するか確認
            try:
                cart = Cart.objects.get(session_key=session_key)
                
                # セッション終了後にカートの内容を保持したくない場合、最終アクティビティ時間を確認
                if not self.PERSIST_CART_AFTER_SESSION:
                    # 現在の時間を取得
                    current_time = timezone.now()
                    # セッションに最終アクティビティ時間が含まれているか確認
                    last_activity = request.session.get('last_cart_activity')
                    
                    if last_activity:
                        # datetimeオブジェクトに変換
                        last_activity_time = timezone.datetime.fromisoformat(last_activity)
                        # 30分間（1800秒）アクティビティがないか確認
                        time_diff = (current_time - last_activity_time).total_seconds()
                        if time_diff > 1800:  # 30分
                            # カートを空にする
                            cart.items.all().delete()
                
                # セッション内の最終アクティビティ時間を更新
                request.session['last_cart_activity'] = timezone.now().isoformat()
            except Cart.DoesNotExist:
                # カートが存在しない場合、新しいカートを作成
                cart = Cart.objects.create(session_key=session_key)
                # 初期アクティビティ時間を設定
                request.session['last_cart_activity'] = timezone.now().isoformat()
        return cart
    
    def list(self, request):
        """カートの内容を表示"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    from django.views.decorators.csrf import csrf_exempt
    from django.utils.decorators import method_decorator
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """商品をカートに追加"""
        try:
            novel_id = request.data.get('novel_id')
            quantity = request.data.get('quantity', 1)
            
            if not novel_id:
                return Response({'error': '小説IDは必須です'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return Response({'error': '数量は0より大きくなければなりません'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': '数量は整数でなければなりません'}, status=status.HTTP_400_BAD_REQUEST)
            
            # カートを取得
            cart = self.get_cart(request)
            
            # 小説オブジェクトを取得
            try:
                novel = Novel.objects.get(id=novel_id)
            except Novel.DoesNotExist:
                return Response({'error': '小説が存在しません'}, status=status.HTTP_404_NOT_FOUND)
            
            # カートにすでにその商品が存在するか確認
            cart_item, created = CartItem.objects.get_or_create(cart=cart, novel=novel)
            
            # 商品が既に存在する場合は数量を増やす
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                # 新しい商品の場合は数量を設定
                cart_item.quantity = quantity
                cart_item.save()
            
            # 更新されたカートを返す
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """カート内の商品の数量を更新"""
        try:
            item_id = request.data.get('item_id')
            quantity = request.data.get('quantity')
            
            if not item_id or not quantity:
                return Response({'error': '商品IDと数量は必須です'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                quantity = int(quantity)
                # 数量を減らすために負の数を許可
                if quantity == 0:
                    return Response({'error': '数量は0にすることができません'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': '数量は整数でなければなりません'}, status=status.HTTP_400_BAD_REQUEST)
            
            # カートを取得
            cart = self.get_cart(request)
            
            # カートアイテムを取得
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
            except CartItem.DoesNotExist:
                return Response({'error': 'カートアイテムが存在しません'}, status=status.HTTP_404_NOT_FOUND)
            
            # 数量を更新
            # 正数の場合は数量を増やし、負数の場合は数量を減らす
            new_quantity = cart_item.quantity + quantity
            
            # 数量が1以上であることを確認
            if new_quantity <= 0:
                # 数量が0以下の場合は商品を削除
                cart_item.delete()
            else:
                # それ以外の場合は数量を更新
                cart_item.quantity = new_quantity
                cart_item.save()
            
            # 更新されたカートを返す
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """カートから商品を削除"""
        try:
            item_id = request.query_params.get('item_id')
            
            if not item_id:
                return Response({'error': '商品IDは必須です'}, status=status.HTTP_400_BAD_REQUEST)
            
            # カートを取得
            cart = self.get_cart(request)
            
            # カートアイテムを取得して削除
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                cart_item.delete()
            except CartItem.DoesNotExist:
                return Response({'error': 'カートアイテムが存在しません'}, status=status.HTTP_404_NOT_FOUND)
            
            # 更新されたカートを返す
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """カートを空にする"""
        try:
            # カートを取得
            cart = self.get_cart(request)
            
            # カート内のすべての商品を削除
            cart.items.all().delete()
            
            # 更新されたカートを返す
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
