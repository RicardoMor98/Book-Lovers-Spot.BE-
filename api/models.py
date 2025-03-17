from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('author', 'Author'),
        ('reader', 'Reader'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.TextField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"  # Explicitly set the database table name


class Author(models.Model):
    name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)  # Adding Date of Birth

    class Meta:
        db_table = "authors" 


class Reading(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ Use AutoField for integer ID
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ Ensure author_id is an integer
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Auto sets timestamp on creation

    class Meta:
        db_table = "readings"  # Define table name

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow anonymous users
    reading_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "votes"  # Ensure the table name is "votes" 

    def __str__(self):
        if self.user:
            return f"User {self.user.id} voted on Reading {self.reading_id}"
        return f"Anonymous vote on Reading {self.reading_id}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference User model
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE)  # Reference Reading model
    content = models.TextField()  # Comment text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    class Meta:
        db_table = "comments"  # Table name in the database

    def __str__(self):
        return f"Comment by User {self.user.id} on Reading {self.reading.id}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reading')  # Ensures a user can't favorite the same reading twice
        db_table = "favorites"

    def __str__(self):
        return f"{self.user.username} favorited {self.reading.title}"