from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from community.models import TeamComment


class Command(BaseCommand):
    help = "Create 'community_admins' group and grant can_moderate_comments"

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="community_admins")
        ct = ContentType.objects.get_for_model(TeamComment)
        perm = Permission.objects.get(codename="can_moderate_comments", content_type=ct)
        group.permissions.add(perm)
        self.stdout.write(self.style.SUCCESS("Group 'community_admins' ready with can_moderate_comments."))