import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.services.review_service import review_service
from app.services.database import db
from datetime import datetime, timedelta
import uuid

def clear_existing_data():
    print("Clearing existing data...")
    try:
        db.execute("DELETE FROM feedbacks")
        print("  Deleted feedbacks")
    except Exception as e:
        print(f"  Error clearing feedbacks: {e}")
    try:
        db.execute("DELETE FROM reviews")
        print("  Deleted reviews")
    except Exception as e:
        print(f"  Error clearing reviews: {e}")

def seed_demo_data():
    clear_existing_data()
    print("Seeding demo data...")

    demo_entries = [
        {
            "feedback_text": "Love the new dark mode feature! It's so much easier on my eyes at night.",
            "product": "WebStore",
            "nps_score": 10,
            "user_id": "user-bob-002",
            "categories": ["features"],
            "needs_review": False,
            "assigned_team": "none",
            "status": "resolved",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "kb_references": []
        },
        {
            "feedback_text": "Delivery was super fast! Got my order in 2 days.",
            "product": "MobileApp",
            "nps_score": 10,
            "user_id": "user-emma-005",
            "categories": ["delivery"],
            "needs_review": False,
            "assigned_team": "none",
            "status": "resolved",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=12)).isoformat(),
            "kb_references": []
        },
        {
            "feedback_text": "The checkout process is confusing. I spent 10 minutes trying to find the payment button.",
            "product": "WebStore",
            "nps_score": 4,
            "user_id": "user-alice-001",
            "categories": ["usability"],
            "needs_review": True,
            "assigned_team": "Product Team",
            "status": "resolved",
            "human_response": "Hi Alice, we fixed the checkout flow. The payment button is now more visible.",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "kb_references": []
        },
        {
            "feedback_text": "Your live chat keeps saying 'Connecting...' forever. I just want to know why I was charged twice.",
            "product": "MobileApp",
            "nps_score": 2,
            "user_id": "user-charlie-003",
            "categories": ["billing"],
            "needs_review": True,
            "assigned_team": "Billing Team",
            "status": "resolved",
            "human_response": "Hi Charlie, we resolved the duplicate charge. Refund processed.",
            "created_at": (datetime.now() - timedelta(hours=18)).isoformat(),
            "kb_references": ["Contact Support"]
        },
        {
            "feedback_text": "The product recommendations are not relevant to my interests anymore.",
            "product": "WebStore",
            "nps_score": 5,
            "user_id": "user-diana-004",
            "categories": ["product"],
            "needs_review": False,
            "assigned_team": "none",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
            "kb_references": []
        },
        {
            "feedback_text": "Would be great to have a wishlist feature for saved items.",
            "product": "WebStore",
            "nps_score": 7,
            "user_id": "user-henry-008",
            "categories": ["features"],
            "needs_review": False,
            "assigned_team": "none",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "kb_references": []
        },
        {
            "feedback_text": "The delivery was late, and the installation technician was unprepared. When I asked about warranty, they couldn't answer.",
            "product": "WebStore",
            "nps_score": 2,
            "user_id": "prabhu",
            "categories": ["delivery"],
            "needs_review": True,
            "assigned_team": "Delivery Team",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "kb_references": ["Delivery Timeline", "Installation Process"]
        },
        {
            "feedback_text": "My order arrived 5 days late. The tracking showed it was still in transit even after delivery.",
            "product": "MobileApp",
            "nps_score": 3,
            "user_id": "user-raj-009",
            "categories": ["delivery"],
            "needs_review": True,
            "assigned_team": "Delivery Team",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=4)).isoformat(),
            "kb_references": ["Delivery Timeline"]
        },
        {
            "feedback_text": "I purchased an extended warranty but when I tried to file a claim, I was told my product wasn't eligible.",
            "product": "WebStore",
            "nps_score": 4,
            "user_id": "user-sara-010",
            "categories": ["warranty"],
            "needs_review": True,
            "assigned_team": "Warranty Team",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=8)).isoformat(),
            "kb_references": ["Warranty Information"]
        },
        {
            "feedback_text": "I tried to cancel my order within 24 hours but the system didn't let me.",
            "product": "MobileApp",
            "nps_score": 3,
            "user_id": "user-amy-011",
            "categories": ["cancellation"],
            "needs_review": True,
            "assigned_team": "Billing Team",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=12)).isoformat(),
            "kb_references": ["Cancellation Policy"]
        },
        {
            "feedback_text": "The product arrived damaged and I need to return it.",
            "product": "WebStore",
            "nps_score": 4,
            "user_id": "user-bob-002",
            "categories": ["return"],
            "needs_review": True,
            "assigned_team": "Delivery Team",
            "status": "resolved",
            "human_response": "Hi Bob, pickup arranged. No need to print anything.",
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "kb_references": ["Return Process"]
        },
        {
            "feedback_text": "The assembly instructions were unclear and some parts were missing.",
            "product": "WebStore",
            "nps_score": 5,
            "user_id": "user-raj-009",
            "categories": ["assembly"],
            "needs_review": True,
            "assigned_team": "Product Team",
            "status": "pending",
            "human_response": None,
            "created_at": (datetime.now() - timedelta(hours=3)).isoformat(),
            "kb_references": ["Product Assembly"]
        }
    ]

    for entry in demo_entries:
        feedback_id = vector_store.add_feedback(
            feedback_text=entry["feedback_text"],
            product=entry["product"],
            nps_score=entry["nps_score"],
            user_id=entry["user_id"],
            categories=entry["categories"],
            needs_review=entry.get("needs_review", False),
            assigned_team=entry.get("assigned_team", "none"),
            kb_references=entry.get("kb_references", []),
            created_at=entry["created_at"]
        )

        vector_store.store_embedding(
            feedback_id=feedback_id,
            feedback_text=entry["feedback_text"],
            product=entry["product"],
            categories=entry["categories"],
            nps_score=entry["nps_score"],
            user_id=entry["user_id"],
            created_at=entry["created_at"]
        )

        if entry.get("needs_review") and entry.get("assigned_team") != "none":
            review_service.create_review(
                feedback_id=feedback_id,
                feedback_text=entry["feedback_text"],
                product=entry["product"],
                nps_score=entry["nps_score"],
                categories=entry["categories"],
                assigned_team=entry["assigned_team"],
                original_response="",
                user_id=entry["user_id"],
                is_technical=False,
                duplicate_note=None,
                intent_note=None
            )

            if entry.get("status") == "resolved":
                db.execute(
                    "UPDATE reviews SET status=%s, final_response=%s WHERE feedback_id=%s",
                    ["resolved", entry["human_response"] or "", feedback_id]
                )

    print(f"Seeded {len(demo_entries)} demo entries.")
    print(f"  - Positive (no review): {sum(1 for e in demo_entries if not e.get('needs_review'))}")
    print(f"  - Needs review: {sum(1 for e in demo_entries if e.get('needs_review'))}")

if __name__ == "__main__":
    seed_demo_data()
