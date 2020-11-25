from myapp import models

def create_profile(user):
    profile = models.UserProfile.objects.create(user=user, balance=5000)
    profile.save()
