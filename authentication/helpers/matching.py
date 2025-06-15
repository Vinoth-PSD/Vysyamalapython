from django.core.cache import cache
from authentication import models
from authentication.serializers import MatchingscoreSerializer

# Cache key & TTL settings
MATCHING_SCORE_CACHE_KEY = "matching_score_map"
MATCHING_SCORE_CACHE_TTL = 60 * 60 * 24  # 24 hours

def preload_matching_scores(force_refresh=False):
    """
    Loads all matching scores into cache.
    """
    if not force_refresh and cache.get(MATCHING_SCORE_CACHE_KEY) is not None:
        return
    
    queryset = models.MatchingStarPartner.objects.all()
    serializer = MatchingscoreSerializer(queryset, many=True)
    
    score_map = {}
    
    for item in serializer.data:
        key = (
            str(item['source_star_id']),
            str(item['source_rasi_id']),
            str(item['dest_star_id']),
            str(item['dest_rasi_id']),
            str(item['gender']).lower(),  # Standardize to lowercase
        )
        score_map[key] = int(item.get('match_count', 0))
    
    cache.set(MATCHING_SCORE_CACHE_KEY, score_map, MATCHING_SCORE_CACHE_TTL)
    print(f"Successfully cached {len(score_map)} matching scores")

def get_matching_score_util(source_star_id, source_rasi_id, dest_star_id, dest_rasi_id, gender):
    """
    Returns the matching score from cache with DB fallback.
    """
    if not all([source_star_id, source_rasi_id, dest_star_id, dest_rasi_id, gender]):
        return 0
    
    # Standardize input gender to lowercase
    gender = str(gender).lower()
    
    # Try cache first
    score_map = cache.get(MATCHING_SCORE_CACHE_KEY)
    if score_map is None:
        print("Cache miss - loading matching scores")
        preload_matching_scores()
        score_map = cache.get(MATCHING_SCORE_CACHE_KEY, {})
    
    key = (
        str(source_star_id), 
        str(source_rasi_id), 
        str(dest_star_id), 
        str(dest_rasi_id), 
        gender  # Use already lowercased gender
    )
    
    match_count = score_map.get(key, 0)
    
    # Fallback to DB if not found in cache
    if match_count == 0:
        try:
            match = models.MatchingStarPartner.objects.get(
                source_star_id=source_star_id,
                source_rasi_id=source_rasi_id,
                dest_star_id=dest_star_id,
                dest_rasi_id=dest_rasi_id,
                gender__iexact=gender  # Case-insensitive match
            )
            match_count = match.match_count
            # Update cache for future requests
            score_map[key] = match_count
            cache.set(MATCHING_SCORE_CACHE_KEY, score_map, MATCHING_SCORE_CACHE_TTL)
        except models.MatchingStarPartner.DoesNotExist:
            pass
    
    return 100 if match_count == 15 else match_count * 10