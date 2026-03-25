import asyncio
import uuid
import sys
from datetime import datetime
sys.path.insert(0, ".")
from sqlalchemy import text
from app.database import engine, AsyncSessionLocal
from app.models.base import Base
from app.models.user import User, UserRole, PropertyType, Purpose
from app.models.broker import Broker
from app.models.listing import Listing, ListingType, ListingPurpose, ListingStatus
import app.models.notification  # ensure model is registered
import app.models.wishlist
import app.models.token_blacklist

async def seed_data():
    # Create all tables first (in case notifications table doesn't exist yet)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # TRUNCATE for fast mass deletion
    async with engine.begin() as conn:
        print("Cleaning existing dummy data...")
        await conn.execute(text("TRUNCATE TABLE notifications, broker_assignments, listings, brokers, users CASCADE;"))
        
    async with AsyncSessionLocal() as session:
        # ──────────────────────────────────
        # USERS
        # ──────────────────────────────────
        print("Seeding Users...")
        admin = User(
            email='admin@realestate.local',
            name='Super Admin',
            role=UserRole.admin,
            is_active=True,
            onboarding_complete=True
        )
        broker_user_1 = User(
            email='broker@realestate.local', 
            name='Rajesh Sharma', 
            role=UserRole.broker,
            is_active=True,
            onboarding_complete=True
        )
        broker_user_2 = User(
            email='broker2@realestate.local', 
            name='Priya Mehta', 
            role=UserRole.broker,
            is_active=True,
            onboarding_complete=True
        )
        broker_user_3 = User(
            email='broker3@realestate.local', 
            name='Vikram Patel', 
            role=UserRole.broker,
            is_active=True,
            onboarding_complete=True
        )
        regular_user = User(
            email='user@realestate.local', 
            name='Anita Desai', 
            role=UserRole.user,
            is_active=True,
            onboarding_complete=True,
            location_name='Mumbai',
            lat=19.076,
            lng=72.877,
            budget_min=20000,
            budget_max=200000,
            preferred_type=PropertyType.flat,
            purpose=Purpose.rent,
        )
        regular_user_2 = User(
            email='user2@realestate.local',
            name='Suresh Kumar',
            role=UserRole.user,
            is_active=True,
            onboarding_complete=True,
            location_name='Mumbai',
            lat=19.076,
            lng=72.877,
            budget_min=5000000,
            budget_max=50000000,
            preferred_type=PropertyType.villa,
            purpose=Purpose.buy,
        )
        
        session.add_all([admin, broker_user_1, broker_user_2, broker_user_3, regular_user, regular_user_2])
        await session.commit()
        await session.refresh(broker_user_1)
        await session.refresh(broker_user_2)
        await session.refresh(broker_user_3)

        # ──────────────────────────────────
        # BROKER PROFILES
        # ──────────────────────────────────
        print("Seeding Broker Profiles...")

        # Bandra West area
        bandra_polygon = "POLYGON((72.82 19.04, 72.85 19.04, 72.85 19.07, 72.82 19.07, 72.82 19.04))"
        b_profile_1 = Broker(
            user_id=broker_user_1.id,
            locality_name="Bandra West",
            locality_polygon=f"SRID=4326;{bandra_polygon}",
            verified=True,
            rating=4.8
        )

        # Andheri area
        andheri_polygon = "POLYGON((72.82 19.10, 72.86 19.10, 72.86 19.14, 72.82 19.14, 72.82 19.10))"
        b_profile_2 = Broker(
            user_id=broker_user_2.id,
            locality_name="Andheri West",
            locality_polygon=f"SRID=4326;{andheri_polygon}",
            verified=True,
            rating=4.5
        )

        # Juhu area
        juhu_polygon = "POLYGON((72.81 19.09, 72.84 19.09, 72.84 19.12, 72.81 19.12, 72.81 19.09))"
        b_profile_3 = Broker(
            user_id=broker_user_3.id,
            locality_name="Juhu",
            locality_polygon=f"SRID=4326;{juhu_polygon}",
            verified=True,
            rating=4.9
        )

        session.add_all([b_profile_1, b_profile_2, b_profile_3])
        await session.commit()
        await session.refresh(b_profile_1)
        await session.refresh(b_profile_2)
        await session.refresh(b_profile_3)

        # ──────────────────────────────────
        # LISTINGS (15+ diverse entries)
        # ──────────────────────────────────
        print("Seeding Listings...")
        listings = [
            # ── Bandra listings (Broker 1) ──
            Listing(
                user_id=broker_user_1.id,
                broker_id=b_profile_1.id,
                type=ListingType.flat,
                purpose=ListingPurpose.rent,
                title='Luxury Sea-view 3BHK in Bandra',
                description='A breathtaking 3BHK flat overlooking the Arabian Sea. Features a fully modular kitchen with Bosch appliances, Italian marble flooring, and floor-to-ceiling windows in the master bedroom. The apartment comes with two dedicated parking spots and access to a rooftop infinity pool.',
                price=150000,
                area_sqft=1800,
                bedrooms=3,
                city='Mumbai',
                address='16th Road, Bandra West, Mumbai 400050',
                lat=19.055,
                lng=72.830,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200',
                        'https://images.unsplash.com/photo-1502672260266-1c1e52db06ac?w=1200']
            ),
            Listing(
                user_id=broker_user_1.id,
                broker_id=b_profile_1.id,
                type=ListingType.villa,
                purpose=ListingPurpose.buy,
                title='Spacious Heritage Villa with Pool',
                description='A magnificently restored heritage villa featuring a lush private garden, an outdoor swimming pool, and a covered terrace perfect for entertaining. The property includes 5 spacious bedrooms, each with en-suite bathrooms, a grand living room with original teak wood paneling, and a modern kitchen.',
                price=55000000,
                area_sqft=4500,
                bedrooms=5,
                city='Mumbai',
                address='Pali Hill, Bandra West, Mumbai 400050',
                lat=19.060,
                lng=72.835,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200',
                        'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200']
            ),
            Listing(
                user_id=regular_user.id,
                broker_id=b_profile_1.id,
                type=ListingType.flat,
                purpose=ListingPurpose.rent,
                title='Charming 1BHK Studio in Bandra',
                description='A cozy and well-lit 1BHK studio apartment ideal for young professionals. Located in a quiet lane, walking distance from Bandra station and Linking Road shopping district. The flat features a compact kitchen, a balcony, and plenty of natural light.',
                price=35000,
                area_sqft=550,
                bedrooms=1,
                city='Mumbai',
                address='Hill Road, Bandra West, Mumbai 400050',
                lat=19.058,
                lng=72.832,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=1200']
            ),
            Listing(
                user_id=regular_user_2.id,
                broker_id=b_profile_1.id,
                type=ListingType.flat,
                purpose=ListingPurpose.buy,
                title='Premium 4BHK Penthouse in Bandra',
                description='An expansive penthouse with a private rooftop terrace offering 360° views of the Mumbai skyline and the sea. Features a designer interior with imported Italian marble, a home theater room, a gym, and a jacuzzi on the terrace. Comes with 3 car parks.',
                price=85000000,
                area_sqft=3200,
                bedrooms=4,
                city='Mumbai',
                address='Carter Road, Bandra West, Mumbai 400050',
                lat=19.052,
                lng=72.828,
                status=ListingStatus.verified,
                images=['https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200']
            ),

            # ── Andheri listings (Broker 2) ──
            Listing(
                user_id=broker_user_2.id,
                broker_id=b_profile_2.id,
                type=ListingType.flat,
                purpose=ListingPurpose.rent,
                title='Cozy 2BHK Near Andheri Station',
                description='A well-maintained 2BHK apartment just 5 minutes walk from Andheri station. The society features a garden, children\'s play area, and 24/7 security. The flat is semi-furnished with wardrobes, AC in master bedroom, and a modular kitchen.',
                price=45000,
                area_sqft=850,
                bedrooms=2,
                city='Mumbai',
                address='Four Bungalows, Andheri West, Mumbai 400053',
                lat=19.115,
                lng=72.835,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200']
            ),
            Listing(
                user_id=regular_user.id,
                broker_id=b_profile_2.id,
                type=ListingType.flat,
                purpose=ListingPurpose.buy,
                title='Modern 3BHK with Clubhouse Access',
                description='Brand new 3BHK apartment in a premium gated community. The society boasts a clubhouse, swimming pool, gym, and landscaped gardens. All bedrooms have attached bathrooms and the living room opens onto a large balcony.',
                price=22000000,
                area_sqft=1450,
                bedrooms=3,
                city='Mumbai',
                address='Lokhandwala Complex, Andheri West, Mumbai 400053',
                lat=19.130,
                lng=72.830,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200',
                        'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1200']
            ),
            Listing(
                user_id=broker_user_2.id,
                broker_id=b_profile_2.id,
                type=ListingType.flat,
                purpose=ListingPurpose.rent,
                title='Furnished 1BHK for Working Professionals',
                description='Fully furnished 1BHK apartment perfect for working professionals. Includes a bed, sofa, dining table, washing machine, fridge, and microwave. Located near DN Nagar metro station with excellent connectivity to BKC and Lower Parel.',
                price=28000,
                area_sqft=500,
                bedrooms=1,
                city='Mumbai',
                address='Versova, Andheri West, Mumbai 400061',
                lat=19.125,
                lng=72.825,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200']
            ),
            Listing(
                user_id=regular_user_2.id,
                broker_id=b_profile_2.id,
                type=ListingType.bungalow,
                purpose=ListingPurpose.buy,
                title='Independent Bungalow with Garden',
                description='A rare find — an independent bungalow with a 1200 sqft private garden in the heart of Andheri. The property features 4 bedrooms, a spacious living-dining area, a servant\'s quarter, and covered parking for 2 cars. Recently renovated with modern amenities.',
                price=40000000,
                area_sqft=2800,
                bedrooms=4,
                city='Mumbai',
                address='Model Town, Andheri West, Mumbai 400053',
                lat=19.120,
                lng=72.833,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=1200']
            ),

            # ── Juhu listings (Broker 3) ──
            Listing(
                user_id=admin.id,
                broker_id=b_profile_3.id,
                type=ListingType.bungalow,
                purpose=ListingPurpose.rent,
                title='Modern Family Bungalow Near Juhu Beach',
                description='An architecturally stunning modern bungalow just 2 minutes from Juhu Beach. The open-plan ground floor features floor-to-ceiling glass walls, a gourmet kitchen, and seamless indoor-outdoor flow to the garden. Upstairs, 4 bedrooms with walk-in closets offer privacy and comfort.',
                price=450000,
                area_sqft=3200,
                bedrooms=4,
                city='Mumbai',
                address='Juhu Tara Road, Juhu, Mumbai 400049',
                lat=19.100,
                lng=72.825,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200',
                        'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200']
            ),
            Listing(
                user_id=broker_user_3.id,
                broker_id=b_profile_3.id,
                type=ListingType.flat,
                purpose=ListingPurpose.buy,
                title='Elegant 2BHK in Juhu Scheme',
                description='A thoughtfully designed 2BHK flat in a well-known Juhu cooperative society. The apartment enjoys sea breeze, has vitrified tile flooring, modular kitchen, and ample storage. The society has a swimming pool and tennis court.',
                price=18000000,
                area_sqft=1100,
                bedrooms=2,
                city='Mumbai',
                address='Juhu Scheme, Juhu, Mumbai 400049',
                lat=19.095,
                lng=72.830,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200']
            ),
            Listing(
                user_id=regular_user.id,
                broker_id=b_profile_3.id,
                type=ListingType.villa,
                purpose=ListingPurpose.buy,
                title='Ultra-Luxury Villa in Juhu',
                description='An opulent 6-bedroom villa spread across 6000 sqft with a private pool, landscaped gardens, home cinema, wine cellar, and a rooftop entertainment area with sea views. This trophy property represents the pinnacle of Mumbai luxury living.',
                price=120000000,
                area_sqft=6000,
                bedrooms=6,
                city='Mumbai',
                address='Gulmohar Road, Juhu, Mumbai 400049',
                lat=19.098,
                lng=72.828,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1613977257363-707ba9348227?w=1200',
                        'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200']
            ),

            # ── Unassigned / Pending listings ──
            Listing(
                user_id=regular_user.id,
                type=ListingType.flat,
                purpose=ListingPurpose.buy,
                title='Compact Studio Near BKC',
                description='A smart studio apartment perfect for a single professional or couple. Centrally located near the Bandra-Kurla Complex business district, with easy access to the metro. Features a kitchenette, bathroom, and a balcony. The building has a rooftop gym.',
                price=12000000,
                area_sqft=500,
                bedrooms=1,
                city='Mumbai',
                address='BKC, Mumbai 400051',
                lat=19.065,
                lng=72.865,
                status=ListingStatus.pending,
                images=['https://images.unsplash.com/photo-1502672260266-1c1e52db06ac?w=1200']
            ),
            Listing(
                user_id=regular_user_2.id,
                type=ListingType.land,
                purpose=ListingPurpose.buy,
                title='Prime Plot in Goregaon East',
                description='A 2400 sqft NA plot in a developing area of Goregaon East. Ideal for building a residential bungalow or a small apartment complex. Clear title, all permissions in place. Close proximity to the upcoming metro line.',
                price=35000000,
                area_sqft=2400,
                bedrooms=0,
                city='Mumbai',
                address='Goregaon East, Mumbai 400063',
                lat=19.155,
                lng=72.870,
                status=ListingStatus.pending,
                images=['https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200']
            ),
            Listing(
                user_id=regular_user.id,
                type=ListingType.flat,
                purpose=ListingPurpose.rent,
                title='Budget-Friendly 1RK in Powai',
                description='A tidy 1RK apartment in Powai, great for students and young professionals. Close to IIT Bombay and major IT parks. The building has 24/7 water supply and security. Ideal as a first home in Mumbai.',
                price=15000,
                area_sqft=350,
                bedrooms=1,
                city='Mumbai',
                address='Hiranandani Gardens, Powai, Mumbai 400076',
                lat=19.12,
                lng=72.91,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1560448075-cbc16bb4af8e?w=1200']
            ),
            Listing(
                user_id=admin.id,
                type=ListingType.flat,
                purpose=ListingPurpose.rent,
                title='Spacious 3BHK in Lower Parel',
                description='A generously sized 3BHK apartment in a premium tower in Lower Parel. Walking distance to Phoenix Palladium and major corporate offices. Features wooden flooring, a large balcony, and a fully equipped gym in the building.',
                price=125000,
                area_sqft=1600,
                bedrooms=3,
                city='Mumbai',
                address='Senapati Bapat Marg, Lower Parel, Mumbai 400013',
                lat=19.005,
                lng=72.830,
                status=ListingStatus.active,
                images=['https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=1200']
            ),
        ]
        
        session.add_all(listings)
        await session.commit()
        
        print(f"Database seeded completely! ({len(listings)} listings, 3 brokers, 6 users)")

if __name__ == "__main__":
    asyncio.run(seed_data())
