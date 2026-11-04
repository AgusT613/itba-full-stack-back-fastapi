from fastapi import APIRouter
from src.constants.constants import ITBANK_BRANCH_OFFICES, ITBANK_PREFIX
from src.services.branch_service import BranchServiceDep
from src.utils.text_generation import FakerDep

router = APIRouter(prefix=ITBANK_PREFIX, tags=["branch-offices"])


@router.head("/server-alive")
async def is_server_alive():
    return {"response": "ok"}


@router.get(ITBANK_BRANCH_OFFICES)
async def read_item(branch_service: BranchServiceDep):
    return branch_service.list_branch_offices()


@router.post(ITBANK_BRANCH_OFFICES)
async def create_branch_office(branch_service: BranchServiceDep, fake: FakerDep):
    return branch_service.create_branch_office(fake)


@router.delete(f"{ITBANK_BRANCH_OFFICES}/{{branch_office_id}}")
async def delete_branch_office(branch_office_id: int, branch_service: BranchServiceDep):
    deleted_branch = branch_service.delete_branch_office(branch_office_id)
    return {
        "detail": "Branch office deleted successfully",
        "deleted_branch_office": deleted_branch,
    }
