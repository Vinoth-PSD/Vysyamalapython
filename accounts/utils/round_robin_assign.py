from django.db.models import Q
from accounts.models import User, StateRoundRobin
import random

def assign_user_for_state(state_id):
    if not state_id:
        return None

    state_str = str(state_id)

    # 1. Find admins assigned to this state
    admins = User.objects.filter(
        role_id=1,
        status=1,
        is_deleted=0
    ).filter(
        Q(state=state_str) |
        Q(state__startswith=state_str + ",") |
        Q(state__endswith="," + state_str) |
        Q(state__contains="," + state_str + ",")
    ).order_by("id")

    admins = list(admins)

    # ---------------------------------------------
    # 🟥 CASE 1: No admin has this state → fallback
    # ---------------------------------------------
    if not admins:
        fallback_admins = list(
            User.objects.filter(
                role_id=1, status=1, is_deleted=0
            ).order_by("id")
        )
        if not fallback_admins:
            return None
        
        # Pick any random admin
        random_admin = random.choice(fallback_admins)

        # ⚠️ Do not update StateRoundRobin (very important)
        return random_admin
    # ---------------------------------------------
    # END FALLBACK LOGIC
    # ---------------------------------------------

    # ----------------------
    # 🟩 CASE 2: Round Robin
    # ----------------------
    admin_ids = [adm.id for adm in admins]

    rr_obj, created = StateRoundRobin.objects.get_or_create(
        state_id=state_id,
        defaults={"last_assigned_user": None}
    )

    # First assignment → assign first admin
    if not rr_obj.last_assigned_user:
        next_user = admins[0]
        rr_obj.last_assigned_user = next_user
        rr_obj.save()
        return next_user

    # Continue cycle
    last_id = rr_obj.last_assigned_user.id

    # If last assigned user ID is not in admin list (rare case)
    if last_id not in admin_ids:
        next_user = admins[0]
    else:
        last_index = admin_ids.index(last_id)
        next_index = (last_index + 1) % len(admins)
        next_user = admins[next_index]

    # Update pointer
    rr_obj.last_assigned_user = next_user
    rr_obj.save()

    return next_user