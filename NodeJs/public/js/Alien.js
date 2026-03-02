export default class Alien {
  constructor(scene, x, y) {
    this.scene = scene;

    this.sprite = scene.physics.add.sprite(x, y, "alien");
    this.sprite.body.setAllowGravity(false);
  }

  update(speed, direction) {
    this.sprite.x += speed * direction;
  }

  checkEdges() {
    const bounds = this.scene.physics.world.bounds;
    return (
      this.sprite.x >= bounds.width - this.sprite.width / 2 ||
      this.sprite.x <= this.sprite.width / 2
    );
  }

  dropDown(dropSpeed) {
    this.sprite.y += dropSpeed;
  }

  destroy() {
    this.sprite.destroy();
  }
}
