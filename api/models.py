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