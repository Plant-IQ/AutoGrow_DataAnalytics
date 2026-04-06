"""สคริปต์ insert ข้อมูลทดสอบลง database"""

from datetime import datetime, timedelta
from db.sqlite import engine, SensorReading
from sqlmodel import Session

def seed_sensor_data():
    """สร้าง 168 จุดข้อมูล sensor (24 ชั่วโมง ทุก ๑๐ นาที)"""
    
    with Session(engine) as session:
        now = datetime.utcnow()
        
        # สร้าง 168 records (7 วัน ทุก ๑๐ นาที)
        for i in range(168):
            # คำนวณเวลา (ย้อนหลังมาจากตอนนี้)
            ts = now - timedelta(minutes=10 * (167 - i))
            
            # สร้างข้อมูลแบบค่อย ๆ เปลี่ยน (realistic variation)
            reading = SensorReading(
                ts=ts,
                soil=50 + (i % 20) * 0.5,           # 50-60%
                temp=25 + (i % 15) * 0.3,           # 25-29°C
                humidity=60 + (i % 20) * 0.4,       # 60-68%
                light=300 + (i % 50) * 3,           # 300-450 lux
                stage=2,                             # bloom stage
                stage_name="Bloom",
                spectrum="bloom",
                pump_on=i % 3 == 0,                 # pump ทำงานทุก 3 records
                pump_status="healthy",
                light_hrs_today=12.5,
                harvest_eta_days=15,
                health_score=85 + (i % 10)
            )
            session.add(reading)
        
        session.commit()
        print("✅ สร้าง 168 records แล้ว")

if __name__ == "__main__":
    seed_sensor_data()
