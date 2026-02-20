
from app.models.pyramid import PyramidNode
print("Columns in PyramidNode:")
for column in PyramidNode.__table__.columns:
    print(f"- {column.name}: {column.type}")
