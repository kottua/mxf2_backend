from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from database.models import Premises, RealEstateObject
from database import get_db

premises_router = APIRouter()



@premises_router.post("/bulk", response_model=List[PremisesResponse])
async def create_bulk_premises(request: BulkPremisesCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        reo_ids = {premise.reo_id for premise in request.premises}
        if len(reo_ids) > 1:
            raise HTTPException(status_code=400, detail="All premises must reference the same RealEstateObject")
        reo_id = reo_ids.pop()

        reo = await db.get(RealEstateObject, reo_id)
        if not reo:
            raise HTTPException(status_code=404, detail=f"RealEstateObject with id {reo_id} not found")

        premises_data = [premise.model_dump() for premise in request.premises]

        await db.execute(
            insert(Premises),
            premises_data
        )

        await db.commit()

        result = await db.execute(
            select(Premises).where(Premises.reo_id == reo_id).order_by(Premises.id.desc()).limit(len(premises_data))
        )
        created_premises = result.scalars().all()

        return [PremisesResponse.model_validate(p) for p in created_premises]

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@premises_router.post("/", response_model=PremisesResponse)
async def create_premises(request: PremisesCreate, db: AsyncSession = Depends(get_db)):
    try:
        premises = Premises(**request.dict())
        db.add(premises)
        await db.commit()
        await db.refresh(premises)
        return PremisesResponse.from_orm(premises)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@premises_router.get("/{id}", response_model=PremisesResponse)
async def get_premises(id: int, db: AsyncSession = Depends(get_db)):
    premises = await db.get(Premises, id)
    if not premises:
        raise HTTPException(status_code=404, detail="Premises not found")
    return PremisesResponse.from_orm(premises)

@premises_router.get("/", response_model=List[PremisesResponse])
async def get_all_premises(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Premises))
    premises = result.scalars().all()
    return [PremisesResponse.from_orm(p) for p in premises]

@premises_router.put("/{id}", response_model=PremisesResponse)
async def update_premises(id: int, request: PremisesUpdate, db: AsyncSession = Depends(get_db)):
    premises = await db.get(Premises, id)
    if not premises:
        raise HTTPException(status_code=404, detail="Premises not found")
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(premises, key, value)
    await db.commit()
    await db.refresh(premises)
    return PremisesResponse.from_orm(premises)

@premises_router.delete("/{id}", response_model=bool)
async def delete_premises(id: int, db: AsyncSession = Depends(get_db)):
    premises = await db.get(Premises, id)
    if not premises:
        raise HTTPException(status_code=404, detail="Premises not found")
    await db.delete(premises)
    await db.commit()
    return True