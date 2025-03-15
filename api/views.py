import json
from .models import User
from .models import Author
from .models import Reading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
import jwt
import uuid
import datetime
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
import traceback

@csrf_exempt  # Temporarily disable CSRF for testing
def create_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")  # In production, hash the password!
            role = data.get("role", "reader")  # Default role is "reader" if not provided

            if role not in ["author", "reader"]:
                return JsonResponse({"error": "Invalid role. Choose 'author' or 'reader'."}, status=400)

            # Create and save user in the database
            user = User.objects.create(name=name, email=email, password=password, role=role)
            return JsonResponse({"message": "User created successfully!", "user_id": user.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt 
def authenticate_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Check if user exists
            user = User.objects.filter(email=email).first()

            if user is None:
                return JsonResponse({"error": "User not found"}, status=404)

            # Check password (use check_password if passwords are hashed)
            if user.password == password:  
                return JsonResponse({
                    "message": "Authentication successful",
                    "user_id": user.id,
                    "role": user.role
                }, status=200)
            else:
                return JsonResponse({"error": "Invalid password"}, status=401)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
def create_reading(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # ✅ Debugging

            title = data.get("title")
            content = data.get("content")
            author_id = data.get("author_id")

            # ✅ Validate Input Fields
            if not title or not content or not author_id:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            try:
                author_id = int(author_id)  # Convert to integer
                author = User.objects.get(id=author_id)  # Fetch user from DB
            except ValueError:
                return JsonResponse({"error": "Invalid author_id format"}, status=400)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)

            # ✅ Create a New Reading Entry
            reading = Reading.objects.create(
                title=title,
                content=content,
                author=author
            )

            return JsonResponse({"message": "Reading created successfully", "reading_id": str(reading.id)}, status=201)

        except Exception as e:
            print("❌ ERROR:", traceback.format_exc())  # ✅ Print the full error traceback
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def get_readings(request):
    if request.method == "GET":
        author_id = request.GET.get("author_id")  # Get author_id from query params

        if not author_id:
            return JsonResponse({"error": "author_id is required"}, status=400)

        try:
            author = User.objects.get(id=author_id)
            readings = Reading.objects.filter(author=author).values("id", "title", "content", "created_at")

            return JsonResponse(list(readings), safe=False)
        except User.DoesNotExist:
            return JsonResponse({"error": "Author not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_user_profile(request, user_id):  # Accept user_id from the URL
    if request.method == "GET":
        try:
            user = User.objects.get(id=user_id)
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": getattr(user, "role", "User"),  # Handle if role doesn't exist
                "created_at": user.created_at.isoformat(),
            }
            return JsonResponse(user_data, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)