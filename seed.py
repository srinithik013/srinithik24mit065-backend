from app import app, db, Package
import os

def seed_db():
    with app.app_context():
        # Clear existing packages to avoid duplicates
        db.drop_all()
        db.create_all()

        packages = [
            Package(
                name="Royal Baby Shower",
                price="20000",
                description="Premium themed backdrop, pastel balloon decor, cradle decoration, and welcome banner.",
                image="assets/baby-shower.jpg"
            ),
            Package(
                name="Magic Birthday Party",
                price="15000",
                description="Colorful balloon arch, personalized cake table setup, and party props for all ages.",
                image="assets/birthday.jpg"
            ),
            Package(
                name="Grand Engagement",
                price="35000",
                description="Elegant floral stage backdrop, luxury LED lighting, and romantic table centerpieces.",
                image="assets/engagement.jpg"
            )
        ]

        db.session.bulk_save_objects(packages)
        db.session.commit()
        print(f"Successfully seeded {len(packages)} packages!")

if __name__ == "__main__":
    seed_db()
