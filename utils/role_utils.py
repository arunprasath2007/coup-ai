from typing import Dict, List, Type
from roles.base_role import Role
from roles.duke import Duke
from roles.assassin import Assassin
from roles.captain import Captain
from roles.ambassador import Ambassador
from roles.contessa import Contessa

class RoleUtils:
    # @staticmethod
    # def create_role_from_name(role_name: str) -> Role:
    #     role_classes: Dict[str, Type[Role]] = {
    #         "Duke": Duke,
    #         "Assassin": Assassin,
    #         "Captain": Captain,
    #         "Ambassador": Ambassador,
    #         "Contessa": Contessa
    #     }
    #     role_class = role_classes.get(role_name.capitalize())
    #     if role_class:
    #         return role_class()
    #     else:
    #         raise ValueError(f"Unknown role name: {role_name}")
    
    @staticmethod
    def create_role_from_name(name: str) -> Role:
        role_map = {
            "Duke": Duke,
            "Captain": Captain,
            "Ambassador": Ambassador,
            "Assassin": Assassin,
            "Contessa": Contessa
        }
        return role_map[name]()
        
    @staticmethod
    def get_claimed_role_for_block(action_type: str) -> List[str]:
        block_roles = {
            "foreign_aid": ["Duke"],
            "steal": ["Captain", "Ambassador"],
            "assassinate": ["Contessa"]
        }
        return block_roles.get(action_type.lower(), [])

    @staticmethod
    def get_roles_that_can_block(action_type: str) -> List[str]:
        return RoleUtils.get_claimed_role_for_block(action_type)

    @staticmethod
    def can_role_block_action(role_name: str, action_type: str) -> bool:
        blocking_roles = RoleUtils.get_roles_that_can_block(action_type)
        return role_name in blocking_roles