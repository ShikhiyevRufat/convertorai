class Credit:
    user_credits = {}
    INITIAL_CREDITS = 30

    @classmethod
    def add_user(cls, user_id):
        if user_id not in cls.user_credits:
            cls.user_credits[user_id] = cls.INITIAL_CREDITS

    @classmethod
    def get_credits(cls, user_id):
        return cls.user_credits.get(user_id, 0)

    @classmethod
    def deduct_credits(cls, user_id, amount):
        if cls.user_credits.get(user_id, 0) >= amount:
            cls.user_credits[user_id] -= amount
            return True
        return False

    @classmethod
    def reset_credits(cls, user_id):
        cls.user_credits[user_id] = cls.INITIAL_CREDITS
