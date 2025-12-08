from django.db.models import Q
from accounts.models import User, StateRoundRobin

def assign_user_for_state(state_id):
    if not state_id:
        return None

    state_str = str(state_id)

    # 1. Get admins for this state (order fixed by ID)
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

    if not admins.exists():
        return None

    admins = list(admins)
    admin_ids = [adm.id for adm in admins]

    # 2. Get or create this state's pointer
    rr_obj, created = StateRoundRobin.objects.get_or_create(
        state_id=state_id,
        defaults={"last_assigned_user": None}
    )

    # 3. First assignment → first admin
    if not rr_obj.last_assigned_user:
        next_user = admins[0]
        rr_obj.last_assigned_user = next_user
        rr_obj.save()
        return next_user

    # 4. Continue round robin cycle
    last_id = rr_obj.last_assigned_user.id
    last_index = admin_ids.index(last_id)

    next_index = (last_index + 1) % len(admins)
    next_user = admins[next_index]

    # 5. Update pointer
    rr_obj.last_assigned_user = next_user
    rr_obj.save()

    return next_user