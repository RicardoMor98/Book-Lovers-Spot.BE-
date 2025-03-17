import json
from django.db import models
from .models import User
from .models import Author
from .models import Reading
from .models import Vote
from .models import Comment  # Ensure this import is present
from .models import Favorite
from django.db.models import Count, OuterRef, Subquery, IntegerField, Value
from django.db.models.functions import Coalesce
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
from django.shortcuts import get_object_or_404
import cloudinary.uploader
from .models import UserProfile




def api_home(request):
    return JsonResponse({"message": "Welcome to the API!"})
    
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
            # Get user profile (if it exists)
            profile = UserProfile.objects.filter(user=user).first()
            
            user_data = {
                "id": user.id,
                "name": user.name,  # Use `username` or any other field you want to return
                "email": user.email,
                "role": getattr(user, "role", "User"),  # Handle if role doesn't exist
                "created_at": user.created_at.isoformat(),  # Use `date_joined` for creation time
            }

            # If a profile exists, add the profile picture URL to the response
            if profile:
                user_data["profile_picture"] = profile.profile_picture  # Add profile picture URL
            
            return JsonResponse(user_data, status=200)
        
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def upload_profile_picture(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        if "profile_picture" not in request.FILES:
            return JsonResponse({"error": "No image uploaded"}, status=400)

        file = request.FILES["profile_picture"]

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(file)

        # Store the image URL in the user's profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.profile_picture = upload_result["secure_url"]
        profile.save()

        return JsonResponse({"message": "Profile picture updated", "url": profile.profile_picture}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def view_readings(request):
    if request.method == "GET":
        readings = Reading.objects.all().order_by("-created_at")  # Latest first
        data = [
            {
                "id": reading.id,
                "title": reading.title,
                "content": reading.content,
                "created_at": reading.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for reading in readings
        ]
        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def reading_detail(request, id):
    """Fetch a reading by its ID and return as JSON."""
    reading = get_object_or_404(Reading, id=id)

    # Count total votes
    vote_count = Vote.objects.filter(reading_id=reading.id).count()

    # Check if user has voted (optional)
    
    data = {
        "id": reading.id,
        "title": reading.title,
        "content": reading.content,
        "created_at": reading.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "votes": vote_count,
    }

    return JsonResponse(data)


@csrf_exempt  # Disable CSRF for simplicity (not recommended for production)
def upvote_reading(request, id):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=405)

    try:
        # 🚨 Debugging Log: Print Incoming Data
        print(f"Received request body: {request.body}")

        data = json.loads(request.body)
        user_id = data.get("user_id")  # Extract user_id from request body

        if not user_id:
            return JsonResponse({"message": "User ID is required"}, status=400)

        user = User.objects.get(id=user_id) if user_id else None  # Get user if provided

        # Check if the user has already voted on this reading
        if user and Vote.objects.filter(user=user, reading_id=id).exists():
            return JsonResponse({"message": "You have already upvoted this reading."}, status=400)

        # Insert a new vote into the `votes` table
        vote = Vote.objects.create(user=user, reading_id=id)

        # Count total votes for this reading
        new_vote_count = Vote.objects.filter(reading_id=id).count()

        return JsonResponse({
            "message": "Upvote added successfully.",
            "newVoteCount": new_vote_count,
        }, status=201)

    except User.DoesNotExist:
        return JsonResponse({"message": "Invalid user ID"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON format"}, status=400)



@csrf_exempt
def submit_comment(request, reading_id):
    """Handle storing user comments for a reading."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            content = data.get("content")

            if not user_id or not content:
                return JsonResponse({"error": "User ID and content are required."}, status=400)

            reading = get_object_or_404(Reading, id=reading_id)
            
            # Save comment in DB
            comment = Comment.objects.create(user_id=user_id, reading=reading, content=content)
            
            return JsonResponse({
                "message": "Comment posted successfully",
                "comment": {
                    "id": comment.id,
                    "user_id": comment.user.id,
                    "content": comment.content,
                    "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)



@csrf_exempt
def get_comments(request, reading_id):
    """Fetch all comments for a reading, including user details."""
    comments = Comment.objects.filter(reading_id=reading_id).order_by("-created_at")

    data = [
        {
            "id": comment.id,
            "user": {
                "id": comment.user.id,
                "username": comment.user.name,
                "email": comment.user.email,
               
                # Add more user fields if necessary
            },
            "content": comment.content,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for comment in comments
    ]

    return JsonResponse(data, safe=False)



@csrf_exempt
def toggle_favorite(request, reading_id):
    """Add or remove a reading from a user's favorites."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            user = User.objects.get(id=user_id)
            reading = Reading.objects.get(id=reading_id)

            favorite, created = Favorite.objects.get_or_create(user=user, reading=reading)

            if created:
                return JsonResponse({"message": "Added to favorites", "favorited": True})
            else:
                favorite.delete()
                return JsonResponse({"message": "Removed from favorites", "favorited": False})

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Reading.DoesNotExist:
            return JsonResponse({"error": "Reading not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            user = User.objects.get(id=user_id)
            reading = Reading.objects.get(id=reading_id)

            favorite = Favorite.objects.filter(user=user, reading=reading)
            if favorite.exists():
                favorite.delete()
                return JsonResponse({"message": "Removed from favorites", "favorited": False})
            else:
                return JsonResponse({"error": "Favorite not found"}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Reading.DoesNotExist:
            return JsonResponse({"error": "Reading not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def check_favorite_status(request, reading_id):
    """Check if a reading is favorited by the user."""
    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "User ID required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
        favorited = Favorite.objects.filter(user=user, reading_id=reading_id).exists()
        return JsonResponse({"favorited": favorited})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)



@csrf_exempt
def get_favorites(request):
    """Fetch all favorite readings for a user."""
    if request.method == "GET":
        user_id = request.GET.get("user_id")  # Get user_id from query params

        if not user_id:
            return JsonResponse({"error": "User ID is required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
            favorites = Favorite.objects.filter(user=user).select_related("reading")

            # Prepare response data
            favorite_readings = [
                {
                    "id": fav.reading.id,
                    "title": fav.reading.title,
                    "content": fav.reading.content,
                    "created_at": fav.reading.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for fav in favorites
            ]

            return JsonResponse({"favorites": favorite_readings}, status=200)
        
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_newreadings(request):
    filter_option = request.GET.get("filter", "title")
    query = request.GET.get("query", "")

    # Subquery to count votes for each Reading
    vote_count_subquery = Vote.objects.filter(reading_id=OuterRef('id')) \
        .values('reading_id') \
        .annotate(count=Count('id')) \
        .values('count')

    # Annotate vote count, replacing NULL with 0
    readings = Reading.objects.annotate(
        vote_count=Coalesce(Subquery(vote_count_subquery, output_field=IntegerField()), Value(0))
    )

    # Apply search filter if query is present
    if query:
        readings = readings.filter(title__icontains=query)

    # Sorting based on the filter option
    if filter_option == "votes":
        readings = readings.order_by("-vote_count", "-created_at")  # Highest votes first, then newest
    elif filter_option == "date":
        readings = readings.order_by("-created_at")  # Newest first
    else:
        readings = readings.order_by("title")  # Alphabetical order

    # Convert queryset to JSON response
    data = [
        {
            "id": reading.id,
            "title": reading.title,
            "content": reading.content,
            "votes": reading.vote_count,  # Now it will always be an integer
            "created_at": reading.created_at,
        }
        for reading in readings
    ]

    return JsonResponse({"readings": data}, safe=False)