import fastapi
from fastapi import HTTPException
import database
import contacts.schema as schema
import contacts.model as model
from datetime import datetime, timedelta
import auth.service

router = fastapi.APIRouter(prefix="/contacts", tags=["Contacts"])
auth_service = auth.service.Auth()

@router.get("/")
async def root(
    db=fastapi.Depends(database.get_database),
    user = fastapi.Depends(auth_service.get_user)
)-> list[model.ContactResponse]:
    
    return [contact for contact in db.query(model.ContactModel).filter(schema.Contacts.user_id == user.id).all()]

@router.get("/find/{contact_id}")
async def get_by_id(
    contact_id: int,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
) -> model.ContactResponse:
    contact = db.query(schema.Contacts).filter(
        schema.Contacts.id == contact_id,
        schema.Contacts.user_id == user.id
    ).first()
    
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact

@router.post("/")
async def post_root(
    contact: model.ContactModel,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
)-> model.ContactModel:
    new_contact = schema.Contacts(user_id=user.id,**contact.__dict__)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact

@router.delete("/{contact_id}")
async def del_by_id(contact_id : int,   
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
):
    contact = db.query(schema.Contacts).filter(schema.Contacts.id == contact_id,schema.Contacts.user_id == user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()

    return {"message": "Contact deleted"}

@router.patch("/{contact_id}")
async def patch_contact(contact_id:int,
    contact_data: model.ContactUpdate,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
) -> model.ContactResponse:
    contact = db.query(schema.Contacts).filter(schema.Contacts.id == contact_id, schema.Contacts.user_id == user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in contact_data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact

@router.get("/search")
async def search_contacts(
    name: str = None,
    surename: str = None,
    email: str = None,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
) -> list[model.ContactResponse]:
    query = db.query(schema.Contacts).filter(schema.Contacts.id == user.id)
    
    if name:
        query = query.filter(schema.Contacts.name == name)
    if surename:
        query = query.filter(schema.Contacts.surename == surename)
    if email:
        query = query.filter(schema.Contacts.email == email)
    
    results = query.all()
    return results

@router.get("/upcoming-birthdays")
async def get_upcoming_birthdays(
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
)-> list[model.ContactResponse]:
    today = datetime.today().date()
    upcoming_date = datetime.today().date() + timedelta(days=7)

    contacts_with_upcoming_birthdays = db.query(schema.Contacts).filter(
        schema.Contacts.user_id == user.id,
        schema.Contacts.date_of_birth.between(today, upcoming_date)
    ).all()

    return contacts_with_upcoming_birthdays