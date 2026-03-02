export default class Settings{
    constructor(){
        this.shipSpeed=300;
        this.bulletsAllowed=3;
        this.bulletSpeed=500;
        this.alienSpeed=2;
        this.speedIncrease=0.5;
    }
    increaseSpeed() {
  this.alienSpeed += this.speedIncrease;
  this.shipSpeed += this.shipSpeedIncrease;       // 🔴 NEW
  this.bulletSpeed += this.bulletSpeedIncrease;   // 🔴 NEW
}

}
