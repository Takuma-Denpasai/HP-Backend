# カスタマイズ元のcreatesuperuserをインポート
from django.contrib.auth.management.commands import createsuperuser
# 引数エラー時に使用するエラー
from django.core.management import CommandError
 
 
class Command(createsuperuser.Command):
    # --helpもしくは-hでヘルプを呼び出したときに表示される文言
    help = "Create a superuser with a password non-interactively"
 
    # --password という引数を追加
    # usernameやemailはcreatesuperuserにデフォルトであるため、追加不要
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help="Specifies the password for the superuser.",
        )
 
    # コマンドのメインの処理
    def handle(self, *args, **options):
        # 引数の値を取得
        options.setdefault("interactive", False)
        username = options.get("username")
        email = options.get("email")
        password = options.get("password")
        database = options.get("database")
 
        # username,email,passwordが指定されていない場合
        # エラーを出す
        if not (username and email and password):
            raise CommandError(
                "--username, --email and --password are required options"
            )
 
        # 引数から受け取った値を格納
        user_data = {
            "username": username,
            "email": email,
            "password": password,
        }
 
        # usernameをもとにDBに存在しているか確認
        exists = (
            self.UserModel._default_manager.db_manager(database)
            .filter(is_superuser=True)
            .exists()
        )
        # 存在していなければ、superuserを作成
        if not exists:
            self.UserModel._default_manager.db_manager(
                database
            ).create_superuser(**user_data)