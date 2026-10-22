package lessons.kt_07_03
fun main() {
    val nickname: String? = "小林"
    if (nickname != null) {
        println(nickname.length)
    } else {
        println("没有昵称")
    }
}
